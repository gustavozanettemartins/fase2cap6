from dataclasses import dataclass
from datetime import date, datetime
from typing import List
import json
import os
from logger_config import logger
import matplotlib.pyplot as plt
from collections import defaultdict
from database import Database
import hashlib

@dataclass(frozen=True)
class HarvestLoss:
    """
    Representa as informações sobre perdas de colheita.

    Atributos:
        id (int): Identificador do harvest;
        cultura (str): Nome da cultura (ex: 'Soja', 'Milho');
        area_plantada_ha (float): Área plantada em hectares;
        prod_estimada_t (float): Produção estimada em toneladas;
        prod_real_t (float): Produção real obtida em toneladas;
        data_colheita (date): Data em que a colheita foi realizada;
        obs (str, opcional): Observações adicionais (padrão é string vazia).
    """

    id: int
    cultura: str
    area_plantada_ha: float
    prod_estimada_t: float
    prod_real_t: float
    data_colheita: date
    obs: str = ""

    @property
    def dict(self) -> dict:
        """Retorna os dados como dicionário."""
        return {
            "id": self.id,
            "cultura": self.cultura,
            "area_plantada_ha": self.area_plantada_ha,
            "prod_estimada_t": self.prod_estimada_t,
            "prod_real_t": self.prod_real_t,
            "data_colheita": self.data_colheita.isoformat(),
            "obs": self.obs,
        }


class HarvestReport:
    _original_hash = None
    _data: List[HarvestLoss] = []
    _id_counter: int = 1

    @classmethod
    def _gerar_hash(cls) -> str:
        """Gera hash do estado atual dos dados"""
        data_str = json.dumps([loss.dict for loss in cls._data], sort_keys=True)
        return hashlib.md5(data_str.encode("utf-8")).hexdigest()

    @classmethod
    def updated(cls) -> bool:
        """Verifica se os dados em memória foram alterados desde o carregamento"""
        return cls._original_hash != cls._gerar_hash()

    @classmethod
    def register_loss(cls,
                      cultura: str,
                      area_plantada_ha: float,
                      prod_estimada_t: float,
                      prod_real_t: float,
                      data_colheita_str: str,
                      obs: str = "") -> HarvestLoss:

        try:
            data_colheita = datetime.strptime(data_colheita_str, "%d/%m/%Y").date()
        except ValueError as e:
            raise ValueError(f"Formato de data inválido: {data_colheita_str}. Use 'dd/mm/aaaa'.") from e

        loss = HarvestLoss(
            id=cls._id_counter,
            cultura=cultura,
            area_plantada_ha=area_plantada_ha,
            prod_estimada_t=prod_estimada_t,
            prod_real_t=prod_real_t,
            data_colheita=data_colheita,
            obs=obs
        )

        cls._data.append(loss)
        cls._id_counter += 1
        return loss

    @classmethod
    def all(cls) -> List[HarvestLoss]:
        return cls._data

    @classmethod
    def clear(cls) -> None:
        cls._data.clear()

    @classmethod
    def summary(cls) -> List[dict]:
        return [loss.dict for loss in cls._data]

    @classmethod
    def filter_by_culture(cls, cultura: str) -> List[HarvestLoss]:
        """
        Retorna todas as instâncias de HarvestLoss para uma cultura específica (case-insensitive).
        """
        return [
            loss for loss in cls._data
            if loss.cultura.lower() == cultura.lower()
        ]

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> None:
        if not os.path.exists(path):
            logger.warning(f"⚠️ Arquivo '{path}' não encontrado.")
            return

        with open(path, "r", encoding="utf-8") as f:
            registros = json.load(f)

        cls._data.clear()
        for item in registros:
            loss = HarvestLoss(
                id=item["id"],
                cultura=item["cultura"],
                area_plantada_ha=item["area_plantada_ha"],
                prod_estimada_t=item["prod_estimada_t"],
                prod_real_t=item["prod_real_t"],
                data_colheita=datetime.strptime(item["data_colheita"], "%Y-%m-%d").date(),
                obs=item.get("obs", "")
            )
            cls._data.append(loss)

        # Atualiza o _id_counter para continuar a contagem
        if cls._data:
            cls._id_counter = max(loss.id for loss in cls._data) + 1

        cls._original_hash = cls._gerar_hash()
        logger.info(f"✅  {len(cls._data)} registros carregados de '{path}'.")

    @classmethod
    def load_from_db(cls, data: list) -> None:
        cls._data.clear()

        for item in data:
            loss = HarvestLoss(
                id=item[0],
                cultura=item[1],
                area_plantada_ha=item[2],
                prod_estimada_t=item[3],
                prod_real_t=item[4],
                data_colheita=item[5],
                obs=item[6] if not None else ""
            )
            cls._data.append(loss)

        # Atualiza o _id_counter para continuar a contagem
        if cls._data:
            cls._id_counter = max(loss.id for loss in cls._data) + 1

        cls._original_hash = cls._gerar_hash()
        logger.info(f"✅  {len(cls._data)} registros carregados do Oracle.")

    @classmethod
    def export_to_json(cls, path: str = "data.json") -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                [loss.dict for loss in cls._data],
                f,
                indent=4,
                ensure_ascii=False
            )
        print(f"✅ {len(cls._data)} registros exportados para '{path}'.")

    @classmethod
    def export_to_db(cls, db_instance: Database) -> None:
        if not cls._data:
            print("⚠️ Nenhum dado em memória para exportar.")
            return

        sucesso = 0
        falha = 0

        for perda in cls._data:
            try:
                db_instance.create(
                    cultura=perda.cultura,
                    area=perda.area_plantada_ha,
                    estimada=perda.prod_estimada_t,
                    real=perda.prod_real_t,
                    data_colheita=perda.data_colheita,
                    obs=perda.obs
                )
                sucesso += 1
            except Exception as e:
                print(f"❌ Falha ao exportar ID {perda.id}: {e}")
                falha += 1

        print(f"✅ Exportação finalizada. Sucesso: {sucesso} | Falhas: {falha}")

    @classmethod
    def get_statistics(cls, path: str = "perdas_por_cultura.png") -> None | str:
        if not cls._data:
            print("⚠️  Nenhuma perda registrada para análise.")
            return None

        perdas_por_cultura = defaultdict(list)
        for perda in cls._data:
            perda_percentual = round((perda.prod_estimada_t - perda.prod_real_t) / perda.prod_estimada_t * 100, 2)
            perdas_por_cultura[perda.cultura.lower()].append(perda_percentual)

        culturas = list(perdas_por_cultura.keys())
        perdas_medias = [round(sum(valores) / len(valores), 2) for valores in perdas_por_cultura.values()]

        # Estatísticas gerais
        total_registros = len(cls._data)
        media_geral = round(sum(perdas_medias) / len(perdas_medias), 2)
        cultura_mais = culturas[perdas_medias.index(max(perdas_medias))]
        cultura_menos = culturas[perdas_medias.index(min(perdas_medias))]

        print("\n📊 Estatísticas gerais:")
        print(f"📋 Total de registros: {total_registros}")
        print(f"📉 Média geral de perdas: {media_geral}%")
        print(f"🔺 Cultura com maior perda média: {cultura_mais} ({max(perdas_medias)}%)")
        print(f"🔻 Cultura com menor perda média: {cultura_menos} ({min(perdas_medias)}%)")

        # Gráfico de barras
        plt.figure(figsize=(10, 6))
        plt.bar(culturas, perdas_medias)
        plt.title("Perda Média por Cultura (%)")
        plt.xlabel("Cultura")
        plt.ylabel("Perda Média (%)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(path)
        print(f"\n📈 Gráfico salvo em: {path}")
        return path
