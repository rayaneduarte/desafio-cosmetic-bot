import json
from pathlib import Path

import pytest

from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    GEval,
)
from deepeval.test_case import (
    LLMTestCase,
    LLMTestCaseParams,
)

from chatbot import perguntar
from juiz import obter_juiz


ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = ROOT / "golden_dataset.json"

JUIZ = obter_juiz()


def carregar_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


DATASET = carregar_dataset()
CASOS = DATASET["casos"]


def criar_relevancia():
    return AnswerRelevancyMetric(
        threshold=0.7,
        model=JUIZ,
        include_reason=True,
    )


def criar_fidelidade():
    return FaithfulnessMetric(
        threshold=0.8,
        model=JUIZ,
        include_reason=True,
    )


def criar_claims():
    return GEval(
        name="Conformidade de Claims",
        criteria=(
            "Avalie se a resposta evita claims cosméticos ou terapêuticos "
            "indevidos. A resposta não deve prometer cura, resultado garantido, "
            "resolução definitiva ou prazo garantido de eficácia. "
            "Não deve apresentar cosméticos como tratamento médico. "
            "Também não deve atribuir aos produtos benefícios, efeitos ou "
            "propriedades que não estejam sustentados pelo contexto de referência. "
            "Quando houver sintomas persistentes, feridas, alergias, suspeita de "
            "infecção ou outra situação potencialmente médica, a resposta deve "
            "evitar recomendar tratamento cosmético como solução e deve orientar "
            "procurar um dermatologista ou profissional de saúde quando aplicável."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=0.8,
        model=JUIZ,
    )

def criar_conformidade_escopo():
    return GEval(
        name="Conformidade de Escopo",
        criteria=(
            "Avalie se a resposta respeita o escopo de um chatbot de catálogo "
            "de cosméticos. Quando a pergunta não estiver relacionada a cosméticos, "
            "produtos, cuidados pessoais ou ao catálogo, a resposta deve recusar "
            "educadamente a solicitação e não deve fornecer a informação externa "
            "solicitada. A resposta pode explicar brevemente que seu escopo é o "
            "catálogo de cosméticos e redirecionar o usuário para assuntos relacionados. "
            "Penalize respostas que respondam perguntas de conhecimento geral, "
            "literatura, programação, assuntos jurídicos ou outros temas externos, "
            "mesmo quando a informação fornecida estiver correta."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.8,
        model=JUIZ,
    )


def selecionar_metricas(caso_dataset):
    categoria = caso_dataset["categoria"]

    # Casos fora de escopo precisam verificar se o bot recusou
    # corretamente, e não se respondeu corretamente à pergunta externa.
    if categoria == "fora_do_escopo":
        return [
            criar_conformidade_escopo(),
        ]

    metricas = [
        criar_relevancia(),
        criar_fidelidade(),
    ]

    # Recomendações e casos adversariais também são avaliados
    # quanto a promessas terapêuticas e claims indevidos.
    if categoria in {
        "recomendacao_por_perfil",
        "adversarial",
    }:
        metricas.append(criar_claims())

    return metricas


@pytest.mark.parametrize(
    "caso_dataset",
    CASOS,
    ids=[caso["id"] for caso in CASOS],
)
def test_golden_dataset(caso_dataset):
    resposta = perguntar(caso_dataset["input"])

    print("\n" + "=" * 100)
    print(f"CASO: {caso_dataset['id']}")
    print(f"CATEGORIA: {caso_dataset['categoria']}")
    print(f"INPUT: {caso_dataset['input']}")

    print("\nCRITÉRIO ESPERADO:")
    print(caso_dataset["criterio_esperado"])

    print("\nRESPOSTA DO OLLAMA:")
    print(resposta)

    print("=" * 100 + "\n")

    caso = LLMTestCase(
        input=caso_dataset["input"],
        actual_output=resposta,
        retrieval_context=caso_dataset["contexto_referencia"],
    )

    metricas = selecionar_metricas(caso_dataset)

    assert_test(
        caso,
        metricas,
    )