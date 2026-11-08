import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import {
  AlertasResposta,
  DespensaDetalhes,
  Item,
  ListaComprasResposta,
  SolicitacaoAdesao,
  SugestaoReceitasResposta,
  Usuario,
} from '../types';

// Altere para o IP local do seu computador na rede Wi-Fi ao testar no celular físico (ex: http://192.168.1.100:8000)
// No emulador Android, 10.0.2.2 aponta para o localhost do computador host
const API_URL = 'http://10.0.2.2:8000';

export const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

// Interceptor para injetar o Token JWT automaticamente em todas as chamadas
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('@despensa_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  async salvarToken(token: string): Promise<void> {
    await AsyncStorage.setItem('@despensa_token', token);
  },

  async obterToken(): Promise<string | null> {
    return await AsyncStorage.getItem('@despensa_token');
  },

  async removerToken(): Promise<void> {
    await AsyncStorage.removeItem('@despensa_token');
  },

  async login(email: string, senha: string) {
    const response = await api.post('/auth/login', { email, senha });
    if (response.data.access_token) {
      await authService.salvarToken(response.data.access_token);
    }
    return response.data;
  },

  async cadastro(nome: string, email: string, senha: string, nomeDespensa: string) {
    const response = await api.post('/auth/cadastro', {
      nome,
      email,
      senha,
      nome_despensa: nomeDespensa,
    });
    return response.data;
  },

  async verificarCodigo(email: string, codigo: string) {
    const response = await api.post('/auth/verificar-codigo', { email, codigo });
    if (response.data.access_token) {
      await authService.salvarToken(response.data.access_token);
    }
    return response.data;
  },

  async reenviarCodigo(email: string) {
    const response = await api.post('/auth/reenviar-codigo', { email });
    return response.data;
  },

  async loginGoogle(idToken: string, nomeDespensa?: string) {
    const response = await api.post('/auth/google', {
      id_token: idToken,
      nome_despensa: nomeDespensa || 'Nossa Despensa',
    });
    if (response.data.access_token) {
      await authService.salvarToken(response.data.access_token);
    }
    return response.data;
  },

  async me(): Promise<Usuario> {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const itensService = {
  async listar(): Promise<Item[]> {
    const response = await api.get('/itens');
    return response.data;
  },

  async cadastrar(item: {
    nome: string;
    quantidade: number;
    quantidade_minima: number;
    local: string;
    obs?: string;
  }): Promise<Item> {
    const response = await api.post('/itens', item);
    return response.data;
  },

  async adicionarEstoque(itemId: number, quantidade: number): Promise<Item> {
    const response = await api.patch(`/itens/${itemId}/adicionar`, { quantidade });
    return response.data;
  },

  async removerEstoque(itemId: number, quantidade: number): Promise<Item> {
    const response = await api.patch(`/itens/${itemId}/remover`, { quantidade });
    return response.data;
  },

  async deletar(itemId: number): Promise<void> {
    await api.delete(`/itens/${itemId}`);
  },
};

export const comprasService = {
  async listar(): Promise<ListaComprasResposta> {
    const response = await api.get('/compras');
    return response.data;
  },

  async obterAlertas(): Promise<AlertasResposta> {
    const response = await api.get('/alertas');
    return response.data;
  },
};

export const aiService = {
  async sugerirReceitas(): Promise<SugestaoReceitasResposta> {
    const response = await api.post('/receitas/sugerir');
    return response.data;
  },
};

export const despensasService = {
  async obterMinha(): Promise<DespensaDetalhes> {
    const response = await api.get('/despensas/minha');
    return response.data;
  },

  async solicitarEntrada(codigoConvite: string): Promise<{ mensagem: string; sucesso: boolean }> {
    const response = await api.post('/despensas/solicitar-entrada', {
      codigo_convite: codigoConvite,
    });
    return response.data;
  },

  async listarSolicitacoes(): Promise<SolicitacaoAdesao[]> {
    const response = await api.get('/despensas/solicitacoes');
    return response.data;
  },

  async aprovarSolicitacao(id: number): Promise<{ mensagem: string; sucesso: boolean }> {
    const response = await api.post(`/despensas/solicitacoes/${id}/aprovar`);
    return response.data;
  },

  async recusarSolicitacao(id: number): Promise<{ mensagem: string; sucesso: boolean }> {
    const response = await api.post(`/despensas/solicitacoes/${id}/recusar`);
    return response.data;
  },

  async listarMinhasSolicitacoes(): Promise<SolicitacaoAdesao[]> {
    const response = await api.get('/despensas/minhas-solicitacoes');
    return response.data;
  },
};
