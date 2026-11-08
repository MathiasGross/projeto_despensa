import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Clipboard,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { authService, despensasService } from '../services/api';
import { DespensaDetalhes, SolicitacaoAdesao, Usuario } from '../types';

interface PerfilScreenProps {
  onLogout: () => void;
}

export const PerfilScreen: React.FC<PerfilScreenProps> = ({ onLogout }) => {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [despensa, setDespensa] = useState<DespensaDetalhes | null>(null);
  const [solicitacoesPendentes, setSolicitacoesPendentes] = useState<SolicitacaoAdesao[]>([]);
  const [minhasSolicitacoes, setMinhasSolicitacoes] = useState<SolicitacaoAdesao[]>([]);
  const [codigoEntrada, setCodigoEntrada] = useState('');
  const [loading, setLoading] = useState(true);
  const [acaoLoading, setAcaoLoading] = useState(false);

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    setLoading(true);
    try {
      const [u, d, sol, minhas] = await Promise.all([
        authService.me(),
        despensasService.obterMinha().catch(() => null),
        despensasService.listarSolicitacoes().catch(() => []),
        despensasService.listarMinhasSolicitacoes().catch(() => []),
      ]);
      setUsuario(u);
      setDespensa(d);
      setSolicitacoesPendentes(sol);
      setMinhasSolicitacoes(minhas);
    } catch (e) {
      console.error('Erro ao carregar dados do perfil:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCopiarCodigo = () => {
    if (despensa?.codigo_convite) {
      Clipboard.setString(despensa.codigo_convite);
      Alert.alert(
        'Código Copiado!',
        `Código ${despensa.codigo_convite} copiado para a área de transferência. Compartilhe com quem mora com você.`
      );
    }
  };

  const handleSolicitarEntrada = async () => {
    if (!codigoEntrada.trim()) {
      Alert.alert('Atenção', 'Digite o código da despensa que deseja entrar.');
      return;
    }

    setAcaoLoading(true);
    try {
      const res = await despensasService.solicitarEntrada(codigoEntrada.trim());
      Alert.alert('Sucesso', res.mensagem);
      setCodigoEntrada('');
      await carregarDados();
    } catch (error: any) {
      Alert.alert(
        'Não foi possível solicitar',
        error.response?.data?.detail || 'Verifique o código e tente novamente.'
      );
    } finally {
      setAcaoLoading(false);
    }
  };

  const handleAprovar = async (solicitacaoId: number, nomeUsuario: string) => {
    setAcaoLoading(true);
    try {
      const res = await despensasService.aprovarSolicitacao(solicitacaoId);
      Alert.alert('Aprovado!', res.mensagem);
      await carregarDados();
    } catch (error: any) {
      Alert.alert('Erro', error.response?.data?.detail || 'Erro ao aprovar.');
    } finally {
      setAcaoLoading(false);
    }
  };

  const handleRecusar = async (solicitacaoId: number, nomeUsuario: string) => {
    Alert.alert(
      'Recusar Acesso',
      `Tem certeza que deseja recusar o pedido de ${nomeUsuario}? Essa pessoa não terá acesso à sua despensa.`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Recusar',
          style: 'destructive',
          onPress: async () => {
            setAcaoLoading(true);
            try {
              const res = await despensasService.recusarSolicitacao(solicitacaoId);
              Alert.alert('Recusado', res.mensagem);
              await carregarDados();
            } catch (error: any) {
              Alert.alert('Erro', error.response?.data?.detail || 'Erro ao recusar.');
            } finally {
              setAcaoLoading(false);
            }
          },
        },
      ]
    );
  };

  const handleLogout = () => {
    Alert.alert('Sair da Conta', 'Deseja realmente desconectar desta despensa?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Desconectar',
        style: 'destructive',
        onPress: async () => {
          await authService.removerToken();
          onLogout();
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Conta & Despensa</Text>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#10b981" style={{ marginTop: 40 }} />
      ) : (
        <View style={styles.content}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {usuario?.nome ? usuario.nome.slice(0, 2).toUpperCase() : 'ME'}
            </Text>
          </View>

          <Text style={styles.despensaNome}>
            {despensa?.nome || 'Despensa Doméstica'}
          </Text>
          <Text style={styles.despensaSub}>
            {despensa?.e_dono ? '👑 Você é o Proprietário' : '👥 Membro da Despensa'}
          </Text>

          {/* Card: Código Seguro de Compartilhamento */}
          <View style={styles.cardCodigo}>
            <Text style={styles.cardCodigoTitulo}>🔑 Código para Compartilhar:</Text>
            <Text style={styles.cardCodigoSub}>
              Envie para quem mora com você para solicitarem acesso à sua lista:
            </Text>
            <View style={styles.codigoBox}>
              <Text style={styles.codigoTexto}>
                {despensa?.codigo_convite || 'DESP-8X2K9P'}
              </Text>
              <TouchableOpacity
                style={styles.btnCopiar}
                onPress={handleCopiarCodigo}
              >
                <Text style={styles.btnCopiarTexto}>Copiar</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.avisoSeguranca}>
              🛡️ <Text style={{ fontWeight: '700' }}>Segurança Dupla:</Text> Se alguém digitar seu código por engano, não entrará na sua despensa. O acesso só é liberado após a sua aprovação abaixo!
            </Text>
          </View>

          {/* Seção: Solicitações Pendentes (Para o Dono aprovar ou recusar) */}
          {solicitacoesPendentes.length > 0 && (
            <View style={styles.cardPendentes}>
              <View style={styles.badgeAlerta}>
                <Text style={styles.badgeAlertaTexto}>
                  ⚠️ {solicitacoesPendentes.length} Pedido(s) de Acesso Pendente(s)
                </Text>
              </View>
              <Text style={styles.pendentesSub}>
                Confirme quem pode ver e alterar a despensa da sua casa:
              </Text>

              {solicitacoesPendentes.map((sol) => (
                <View key={sol.id} style={styles.solicitacaoItem}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.solicitacaoNome}>
                      {sol.usuario_nome || 'Usuário'}
                    </Text>
                    <Text style={styles.solicitacaoEmail}>
                      {sol.usuario_email || ''}
                    </Text>
                  </View>
                  <View style={styles.botoesAprovacao}>
                    <TouchableOpacity
                      style={styles.btnAprovar}
                      onPress={() => handleAprovar(sol.id, sol.usuario_nome || '')}
                      disabled={acaoLoading}
                    >
                      <Text style={styles.btnAprovarTexto}>✓ Aprovar</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={styles.btnRecusar}
                      onPress={() => handleRecusar(sol.id, sol.usuario_nome || '')}
                      disabled={acaoLoading}
                    >
                      <Text style={styles.btnRecusarTexto}>✕ Recusar</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              ))}
            </View>
          )}

          {/* Card: Membros Atuais */}
          {despensa && despensa.membros && despensa.membros.length > 0 && (
            <View style={styles.cardMembros}>
              <Text style={styles.secaoTitulo}>👥 Membros desta Despensa ({despensa.membros.length})</Text>
              {despensa.membros.map((m) => (
                <View key={m.id} style={styles.membroRow}>
                  <Text style={styles.membroNome}>{m.nome}</Text>
                  <Text style={styles.membroTag}>{m.e_dono ? '👑 Criador' : 'Membro'}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Card: Entrar em outra Despensa via Código */}
          <View style={styles.cardEntrar}>
            <Text style={styles.secaoTitulo}>🏠 Entrar em outra Despensa</Text>
            <Text style={styles.cardCodigoSub}>
              Recebeu um código de convite de alguém? Digite abaixo para solicitar entrada:
            </Text>
            <View style={styles.entrarInputRow}>
              <TextInput
                style={styles.inputCodigo}
                placeholder="Ex: DESP-7K9W2X"
                placeholderTextColor="#64748b"
                value={codigoEntrada}
                onChangeText={setCodigoEntrada}
                autoCapitalize="characters"
              />
              <TouchableOpacity
                style={styles.btnSolicitar}
                onPress={handleSolicitarEntrada}
                disabled={acaoLoading}
              >
                <Text style={styles.btnSolicitarTexto}>Solicitar</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Histórico das minhas solicitações enviadas */}
          {minhasSolicitacoes.length > 0 && (
            <View style={styles.cardMinhas}>
              <Text style={styles.secaoTitulo}>📨 Suas Solicitações Enviadas</Text>
              {minhasSolicitacoes.map((s) => (
                <View key={s.id} style={styles.minhaSolRow}>
                  <Text style={styles.minhaSolNome}>{s.despensa_nome || 'Despensa'}</Text>
                  <Text
                    style={[
                      styles.minhaSolStatus,
                      s.status === 'aprovado'
                        ? { color: '#10b981' }
                        : s.status === 'recusado'
                        ? { color: '#ef4444' }
                        : { color: '#f59e0b' },
                    ]}
                  >
                    {s.status === 'aprovado'
                      ? '✓ Aprovado'
                      : s.status === 'recusado'
                      ? '✕ Recusado'
                      : '⏳ Aguardando Aprovação'}
                  </Text>
                </View>
              ))}
            </View>
          )}

          {/* Dados do Usuário */}
          <View style={styles.cardInfo}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Usuário:</Text>
              <Text style={styles.infoValor}>{usuario?.nome}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>E-mail:</Text>
              <Text style={styles.infoValor}>{usuario?.email}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Status da Conta:</Text>
              <Text style={[styles.infoValor, { color: '#10b981' }]}>
                {usuario?.ativo ? '✓ Ativa e Verificada' : 'Pendente'}
              </Text>
            </View>
          </View>

          <TouchableOpacity style={styles.btnLogout} onPress={handleLogout}>
            <Text style={styles.btnLogoutText}>Desconectar da Conta</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  scrollContent: {
    paddingTop: 45,
    paddingBottom: 40,
  },
  header: {
    paddingHorizontal: 16,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#1e293b',
  },
  headerTitle: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: '800',
  },
  content: {
    padding: 16,
    alignItems: 'center',
  },
  avatar: {
    width: 66,
    height: 66,
    borderRadius: 33,
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    borderWidth: 2,
    borderColor: '#10b981',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
    marginTop: 6,
  },
  avatarText: {
    color: '#10b981',
    fontSize: 20,
    fontWeight: '800',
  },
  despensaNome: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '800',
  },
  despensaSub: {
    color: '#94a3b8',
    fontSize: 12,
    marginTop: 2,
  },
  cardCodigo: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: '#334155',
    marginTop: 18,
  },
  cardCodigoTitulo: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '700',
  },
  cardCodigoSub: {
    color: '#94a3b8',
    fontSize: 12,
    marginTop: 4,
    marginBottom: 10,
  },
  codigoBox: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#0f172a',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#10b981',
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  codigoTexto: {
    color: '#10b981',
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: 2,
  },
  btnCopiar: {
    backgroundColor: '#10b981',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  btnCopiarTexto: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
  },
  avisoSeguranca: {
    color: '#cbd5e1',
    fontSize: 11,
    marginTop: 10,
    lineHeight: 16,
  },
  cardPendentes: {
    backgroundColor: 'rgba(245, 158, 11, 0.08)',
    borderRadius: 16,
    padding: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: 'rgba(245, 158, 11, 0.3)',
    marginTop: 16,
  },
  badgeAlerta: {
    backgroundColor: 'rgba(245, 158, 11, 0.2)',
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 6,
  },
  badgeAlertaTexto: {
    color: '#f59e0b',
    fontSize: 12,
    fontWeight: '700',
  },
  pendentesSub: {
    color: '#94a3b8',
    fontSize: 12,
    marginBottom: 12,
  },
  solicitacaoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#334155',
  },
  solicitacaoNome: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '700',
  },
  solicitacaoEmail: {
    color: '#94a3b8',
    fontSize: 11,
    marginTop: 2,
  },
  botoesAprovacao: {
    flexDirection: 'row',
    gap: 8,
  },
  btnAprovar: {
    backgroundColor: '#10b981',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  btnAprovarTexto: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '700',
  },
  btnRecusar: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ef4444',
  },
  btnRecusarTexto: {
    color: '#ef4444',
    fontSize: 11,
    fontWeight: '700',
  },
  cardMembros: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: '#334155',
    marginTop: 16,
  },
  secaoTitulo: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 10,
  },
  membroRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  membroNome: {
    color: '#cbd5e1',
    fontSize: 13,
  },
  membroTag: {
    color: '#38bdf8',
    fontSize: 11,
    fontWeight: '600',
  },
  cardEntrar: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: '#334155',
    marginTop: 16,
  },
  entrarInputRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 6,
  },
  inputCodigo: {
    flex: 1,
    backgroundColor: '#0f172a',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#334155',
    color: '#ffffff',
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 13,
  },
  btnSolicitar: {
    backgroundColor: '#38bdf8',
    borderRadius: 10,
    paddingHorizontal: 16,
    justifyContent: 'center',
  },
  btnSolicitarTexto: {
    color: '#0f172a',
    fontSize: 13,
    fontWeight: '700',
  },
  cardMinhas: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: '#334155',
    marginTop: 16,
  },
  minhaSolRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  minhaSolNome: {
    color: '#ffffff',
    fontSize: 13,
  },
  minhaSolStatus: {
    fontSize: 11,
    fontWeight: '700',
  },
  cardInfo: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: '#334155',
    marginVertical: 16,
    gap: 10,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  infoLabel: {
    color: '#94a3b8',
    fontSize: 12,
  },
  infoValor: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  btnLogout: {
    width: '100%',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.3)',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
  },
  btnLogoutText: {
    color: '#ef4444',
    fontSize: 13,
    fontWeight: '700',
  },
});
