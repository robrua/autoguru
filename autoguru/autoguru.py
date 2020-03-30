from typing import Callable, Union, Tuple, List, Dict, Any, Iterable

from starlette.applications import Starlette
from starlette.responses import Response
from starlette.requests import Request
import numpy as np
import requests
import uvicorn

from .model import QuestionAnswerStore, Embedder, NearestNeighbors


class AutoGuru(object):
    def __init__(
        self,
        qa_store: QuestionAnswerStore,
        embedder: Embedder,
        nearest_neighbors: NearestNeighbors,
        distance_to_confidence: Callable[[np.ndarray], np.ndarray] = None,
    ) -> None:
        self._qa_store = qa_store
        self._embedder = embedder
        self._nearest_neighbors = nearest_neighbors
        self._confidence = (
            distance_to_confidence
            if distance_to_confidence is not None
            else lambda distance: distance
        )

    def answer(
        self, question: str, answers: int = 1
    ) -> Union[Tuple[str, float], List[Tuple[str, float]]]:
        embedding = self._embedder.embed(text=question)
        similar_ids, distances = self._nearest_neighbors.get_neighbors(
            vectors=embedding, neighbors=answers
        )
        confidences = self._confidence(distances)

        if answers == 1:
            return self._qa_store.get_answer(id_=similar_ids[0][0]), confidences[0][0]
        return list(zip(self._qa_store.get_answers(ids=similar_ids[0]), confidences[0]))

    def set_answer(self, question: str, answer: str) -> None:
        id_ = self._qa_store.add_answer(question=question, answer=answer)
        embedding = self._embedder.embed(text=question)
        self._nearest_neighbors.add(ids=id_, vectors=embedding)


class AutoGuruContext(Dict[str, Any]):
    def __init__(self, server: "AutoGuruServer", root: str = "", **kwargs) -> None:
        super(AutoGuruContext, self).__init__(**kwargs)
        self._server = server
        self._root = root

    @property
    def server(self) -> "AutoGuruServer":
        return self._server

    @property
    def root(self) -> str:
        return self._root


class AutoGuruServer(object):
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 60120

    def __init__(
        self,
        autoguru: AutoGuru,
        services: Iterable[Callable[[Starlette, AutoGuruContext], None]],
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        verbose: bool = False,
    ) -> None:
        self._context = AutoGuruContext(
            server=self, host=host, port=port, verbose=verbose,
        )

        starlette = Starlette(debug=verbose)
        for service in services:
            service(starlette, self._context)

        self._server = uvicorn.Server(
            uvicorn.Config(
                app=starlette, host=self._context["host"], port=self._context["port"]
            )
        )

    def run(self) -> None:
        self._server.run()

    def stop(self) -> None:
        self._server.should_exit = True


class AutoGuruClient(object):
    def __init__(
        self,
        host: str = AutoGuruServer.DEFAULT_HOST,
        port: int = AutoGuruServer.DEFAULT_PORT,
        context_root: str = "",
    ) -> None:
        self._host = host
        self._port = port
        self._root = context_root

    def stop(self) -> None:
        requests.get(
            "http://{}:{}{}/stop".format(self._host, self._port, self._root)
        ).close()


def control_service(server: Starlette, context: AutoGuruContext) -> None:
    @server.route("{}/stop".format(context.root))
    async def stop(request: Request) -> Response:
        context.server.stop()
        return Response()
