export interface Usuario {
  id: number;
  despensa_id: number;
  nome: string;
  email: string;
  ativo?: boolean;
  codigo_despensa?: string;
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

export interface MembroDespensa {
  id: number;
  nome: string;
  email: string;
  e_dono: boolean;
}

export interface DespensaDetalhes {
  id: number;
  nome: string;
  codigo_convite?: string;
  e_dono: boolean;
  membros: MembroDespensa[];
}

export interface SolicitacaoAdesao {
  id: number;
  despensa_id: number;
  usuario_id: number;
  usuario_nome?: string;
  usuario_email?: string;
  despensa_nome?: string;
  status: 'pendente' | 'aprovado' | 'recusado';
  criado_em?: string;
  respondido_em?: string;
}
