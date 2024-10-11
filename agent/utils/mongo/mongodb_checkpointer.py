from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional, Sequence, Tuple

from langchain_core.runnables import RunnableConfig
from pymongo import MongoClient, UpdateOne
from pymongo.database import Database as MongoDatabase
from pymongo.errors import PyMongoError

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
)

import logging
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

logger = logging.getLogger(name="mongodb")

class MongoDBSaver(BaseCheckpointSaver):
    """A checkpoint saver that stores checkpoints in a MongoDB database."""

    client: MongoClient
    db: MongoDatabase

    def __init__(
        self,
        client: MongoClient,
        db_name: str,
    ) -> None:
        super().__init__()
        self.client = client
        self.db = self.client[db_name]
        self.users = self.client[os.getenv("COALLY_DB_NAME")][os.getenv("USERS_COLLECTION_NAME")]
        self.cvs = self.client[os.getenv("COALLY_DB_NAME")][os.getenv("CVS_COLLECTION_NAME")]

    @classmethod
    @contextmanager
    def from_conn_info(
        cls, *, host: str, port: int, db_name: str
    ) -> Iterator["MongoDBSaver"]:
        client = None
        try:
            client = MongoClient(host=host, port=port)
            yield MongoDBSaver(client, db_name)
        finally:
            if client:
                client.close()

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple from the database.

        This method retrieves a checkpoint tuple from the MongoDB database based on the
        provided config. If the config contains a "checkpoint_id" key, the checkpoint with
        the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
        for the given thread ID is retrieved.

        Args:
            config (RunnableConfig): The config to use for retrieving the checkpoint.

        Returns:
            Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        if checkpoint_id := get_checkpoint_id(config):
            query = {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        else:
            query = {"thread_id": thread_id, "checkpoint_ns": checkpoint_ns}

        result = self.db["checkpoints"].find(query).sort("checkpoint_id", -1).limit(1)
        for doc in result:
            config_values = {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": doc["checkpoint_id"],
            }
            checkpoint = self.serde.loads_typed((doc["type"], doc["checkpoint"]))
            serialized_writes = self.db["checkpoint_writes"].find(config_values)
            pending_writes = [
                (
                    doc["task_id"],
                    doc["channel"],
                    self.serde.loads_typed((doc["type"], doc["value"])),
                )
                for doc in serialized_writes
            ]
            return CheckpointTuple(
                {"configurable": config_values},
                checkpoint,
                self.serde.loads(doc["metadata"]),
                (
                    {
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_ns": checkpoint_ns,
                            "checkpoint_id": doc["parent_checkpoint_id"],
                        }
                    }
                    if doc.get("parent_checkpoint_id")
                    else None
                ),
                pending_writes,
            )

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints from the database.

        This method retrieves a list of checkpoint tuples from the MongoDB database based
        on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).

        Args:
            config (RunnableConfig): The config to use for listing the checkpoints.
            filter (Optional[Dict[str, Any]]): Additional filtering criteria for metadata. Defaults to None.
            before (Optional[RunnableConfig]): If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None.
            limit (Optional[int]): The maximum number of checkpoints to return. Defaults to None.

        Yields:
            Iterator[CheckpointTuple]: An iterator of checkpoint tuples.
        """
        query = {}
        if config is not None:
            query = {
                "thread_id": config["configurable"]["thread_id"],
                "checkpoint_ns": config["configurable"].get("checkpoint_ns", ""),
            }

        if filter:
            for key, value in filter.items():
                query[f"metadata.{key}"] = value

        if before is not None:
            query["checkpoint_id"] = {"$lt": before["configurable"]["checkpoint_id"]}

        result = self.db["checkpoints"].find(query).sort("checkpoint_id", -1)

        if limit is not None:
            result = result.limit(limit)
        for doc in result:
            checkpoint = self.serde.loads_typed((doc["type"], doc["checkpoint"]))
            yield CheckpointTuple(
                {
                    "configurable": {
                        "thread_id": doc["thread_id"],
                        "checkpoint_ns": doc["checkpoint_ns"],
                        "checkpoint_id": doc["checkpoint_id"],
                    }
                },
                checkpoint,
                self.serde.loads(doc["metadata"]),
                (
                    {
                        "configurable": {
                            "thread_id": doc["thread_id"],
                            "checkpoint_ns": doc["checkpoint_ns"],
                            "checkpoint_id": doc["parent_checkpoint_id"],
                        }
                    }
                    if doc.get("parent_checkpoint_id")
                    else None
                ),
            )

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Save a checkpoint to the database.

        This method saves a checkpoint to the MongoDB database. The checkpoint is associated
        with the provided config and its parent config (if any).

        Args:
            config (RunnableConfig): The config to associate with the checkpoint.
            checkpoint (Checkpoint): The checkpoint to save.
            metadata (CheckpointMetadata): Additional metadata to save with the checkpoint.
            new_versions (ChannelVersions): New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"]["checkpoint_ns"]
        checkpoint_id = checkpoint["id"]
        type_, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
        doc = {
            "parent_checkpoint_id": config["configurable"].get("checkpoint_id"),
            "type": type_,
            "checkpoint": serialized_checkpoint,
            "metadata": self.serde.dumps(metadata),
        }
        upsert_query = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
        }
        # Perform your operations here
        self.db["checkpoints"].update_one(upsert_query, {"$set": doc}, upsert=True)
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Store intermediate writes linked to a checkpoint.

        This method saves intermediate writes associated with a checkpoint to the MongoDB database.

        Args:
            config (RunnableConfig): Configuration of the related checkpoint.
            writes (Sequence[Tuple[str, Any]]): List of writes to store, each as (channel, value) pair.
            task_id (str): Identifier for the task creating the writes.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"]["checkpoint_ns"]
        checkpoint_id = config["configurable"]["checkpoint_id"]
        operations = []
        for idx, (channel, value) in enumerate(writes):
            upsert_query = {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
                "task_id": task_id,
                "idx": idx,
            }
            type_, serialized_value = self.serde.dumps_typed(value)
            operations.append(
                UpdateOne(
                    upsert_query,
                    {
                        "$set": {
                            "channel": channel,
                            "type": type_,
                            "value": serialized_value,
                        }
                    },
                    upsert=True,
                )
            )
        self.db["checkpoint_writes"].bulk_write(operations)


    def delete_checkpoints_for_thread(
        self,
        thread_id: str = None
    ) -> None:
        
        query = {
                "thread_id": thread_id
            }
        try:
            resultado = self.db["checkpoints"].delete_many(query)
            logger.info(f'{resultado.deleted_count} deleted checkpoints.')
        except Exception as e:
            logger.error(f"Error deleting checkpoints for thread_id {thread_id}", e)

        try:
            resultado = self.db["checkpoint_writes"].delete_many(query)
            logger.info(f'{resultado.deleted_count} deleted checkpoint_writes.')
        except Exception as e:
            logger.error(f"Error deleting checkpoint_writes for thread_id {thread_id}", e)

    def get_user_resume(
        self,
        user_id: str
    ) -> dict:
        
        try:
            pipeline = [
                {
                    "$match": {"_id": ObjectId(user_id)}
                },
                {
                    "$lookup": {
                        "from": "usercvs",
                        "localField": "cv_file",
                        "foreignField": "_id",
                        "as": "user_cv"
                    }
                },
                {
                    "$unwind": "$user_cv"
                },
                {
                    "$project": {
                        "user_cv": 1
                    }
                }
            ]

            result = self.users.aggregate(pipeline)

            result_list = list(result)

            if not result_list:
                logger.warning(f"Couldn't find user or CV for user id {user_id}")
                return {}
            
            result = result_list[0]['user_cv']

            return {k: str(v) if isinstance(v, ObjectId) else v for k, v in result.items()}

        except PyMongoError as e:
            logger.error(f"Error accessing MongoDB:", e)
            return {}
        except Exception as e:
            logger.error(f"Unexpected error:", e)
            return {}
        
    def save_inputs_for_user(
            self,
            user_id: str = None,
            role: str = None,
            sector: str = None
        ) -> None:

        if user_id is None:
            logger.error("User ID is None")
            return

        document = {
            "role": role,
            "sector": sector
        }

        result = self.db["motivations"].update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": document},
            upsert=True
        )
        if result.upserted_id:
            logger.info(f"Inserted new motivation for user ID {user_id}")
        else:
            logger.info(f"Updated motivation for user ID {user_id}")

    def get_motivation_for_user(
        self,
        user_id
    ) -> dict:
        
        query = {
            "user_id": ObjectId(user_id)
        }

        result = self.db["motivations"].find_one(query)

        if result is None:
            logger.info(f"Couldn't find motivations for user {user_id}")
            return {}
        
        logger.info(f"Motivations found for user {user_id}")
        return {k: str(v) if isinstance(v, ObjectId) else v for k, v in result.items()}