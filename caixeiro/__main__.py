"""Execução da etapa 1 pela linha de comando."""

from .dados import GRAFO_5
from .dados_cameras import PASTA_DADOS
from .dados_grafo_18 import GRAFO_18
from .forca_bruta import resolver
from .integracao import caminhos_minimos, matriz_distancias
from .validacao import (
    validar_caso_dijkstra,
    validar_dijkstra,
    validar_forca_bruta,
    validar_grafo,
    validar_guloso,
)
from .vizinho_mais_proximo import vizinho_mais_proximo


def main() -> None:
    resultado_exato = resolver(GRAFO_5, origem="1")
    print("ETAPA 1 — Força bruta no grafo de 5 pontos")
    print(f"Ciclos candidatos: {resultado_exato.ciclos_candidatos}")
    print(f"Ciclos viáveis: {resultado_exato.ciclos_viaveis}")
    if resultado_exato.custo_minimo is None:
        print("Nenhum ciclo hamiltoniano viável foi encontrado.")
    else:
        print(f"Custo mínimo: {resultado_exato.custo_minimo:g} {GRAFO_5.unidade}")
        print("Rota(s) ótima(s):")
        for rota in resultado_exato.rotas_otimas:
            print("  " + " → ".join(rota))

    print("\nETAPA 2 — Dijkstra no grafo de 18 pontos")
    resultados_por_origem = caminhos_minimos(GRAFO_18)
    da_origem = resultados_por_origem["1"]
    for destino in ("7", "18"):
        caminho = da_origem.caminho_ate(destino)
        caminho_texto = " → ".join(caminho) if caminho else "inalcançável"
        print(f"Câmera 1 → {destino}: custo {da_origem.distancias[destino]:g}; caminho {caminho_texto}")
    print(f"Câmeras alcançáveis a partir de 1: {sum(d < float('inf') for d in da_origem.distancias.values())}/18")

    matriz = matriz_distancias(GRAFO_18, resultados_por_origem)
    guloso = vizinho_mais_proximo(GRAFO_18.vertices, matriz, origem="1")
    print("\nETAPA 3 — Vizinho mais próximo no grafo de 18 pontos")
    if guloso.rota is None:
        print("Não foi possível visitar todas as câmeras e retornar à origem.")
        return
    print("Rota de inspeção: " + " → ".join(guloso.rota))
    print(f"Custo total: {guloso.custo_total:g} {GRAFO_18.unidade}")
    print("Trechos (custo de caminho mínimo):")
    for atual, proximo, custo in guloso.passos:
        caminho = resultados_por_origem[atual].caminho_ate(proximo)
        print(f"  {atual} → {proximo}: {custo:g} [{ ' → '.join(caminho or ()) }]")
    print("Observação: o vizinho mais próximo é uma heurística e não garante o ótimo global.")

    print("\nETAPA 4 — Dados integrados")
    for grafo in (GRAFO_5, GRAFO_18):
        fotos_validas = sum(camera.foto.is_file() for camera in grafo.cameras.values())
        print(f"Grafo de {len(grafo.vertices)} pontos: {fotos_validas}/{len(grafo.vertices)} câmeras com foto")
        print("  " + ", ".join(
            f"{identificador}={camera.foto.relative_to(PASTA_DADOS)}"
            for identificador, camera in grafo.cameras.items()
        ))

    print("\nETAPA 5 — Validação dos grafos e algoritmos")
    verificacoes = [
        *validar_grafo(GRAFO_5, origem="1"),
        *validar_grafo(GRAFO_18, origem="1"),
        *validar_forca_bruta(GRAFO_5, resultado_exato),
        *validar_caso_dijkstra(),
        *validar_guloso(GRAFO_18.vertices, matriz, guloso),
    ]
    erros_dijkstra = [
        erro
        for origem, resultado in resultados_por_origem.items()
        for erro in validar_dijkstra(GRAFO_18, resultado)
    ]
    if erros_dijkstra:
        verificacoes.extend(erros_dijkstra)
    else:
        verificacoes.append("OK: Distâncias e caminhos reconstruídos por Dijkstra conferem para todas as origens.")
    if GRAFO_5.peso("1", "3") is None and GRAFO_5.peso("2", "5") is None:
        verificacoes.append("OK: Arestas ausentes do grafo de 5 pontos continuam ausentes nos dados.")
    else:
        verificacoes.append("ERRO: Uma aresta ausente do grafo de 5 pontos foi inventada.")
    for verificacao in verificacoes:
        print(f"  {verificacao}")
    if any(verificacao.startswith("ERRO:") for verificacao in verificacoes):
        raise SystemExit("Validação concluída com erro.")
    print("Todas as validações foram concluídas com sucesso.")


if __name__ == "__main__":
    main()
