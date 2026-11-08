export interface Usuario {
  id: number;
  despensa_id: number;
  nome: string;
  email: string;
  criado_em?: string;
}

export interface Item {
  id: number;
  despensa_id: number;
  nome: string;
  quantidade: number;
  quantidade_minima: number;
  local: string;
  obs: string;
}

export interface ItemCompra {
  item_id: number;
  nome: string;
  quantidade_atual: number;
  quantidade_minima: number;
  quantidade_sugerida: number;
  local: string;
  obs: string;
}

export interface ListaComprasResposta {
  itens: ItemCompra[];
  total_itens: number;
  texto_whatsapp: string;
}

export interface AlertasResposta {
  zerados: Item[];
  acabando: Item[];
  total_alertas: number;
}

export interface IngredienteReceita {
  nome: string;
  quantidade_estimada: string;
  disponivel_em_casa: boolean;
}

export interface Receita {
  titulo: string;
  tempo_minutos: number;
  porcoes: number;
  dificuldade: string;
  descricao: string;
  ingredientes: IngredienteReceita[];
  passo_a_passo: string[];
}

export interface SugestaoReceitasResposta {
  receitas: Receita[];
  total_ingredientes_utilizados: number;
  mensagem: string;
}
