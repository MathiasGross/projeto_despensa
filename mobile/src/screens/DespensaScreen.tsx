import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Modal,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { itensService } from '../services/api';
import { Item } from '../types';

const CATEGORIAS = [
  'Todos',
  'Armário',
  'Geladeira',
  'Freezer',
  'Lavanderia',
  'Limpeza',
];

const SUGESTOES_CATALOGO = [
  'Arroz Tipo 1',
  'Café em Pó',
  'Leite Integral',
  'Ovos',
  'Sabão em Pó',
  'Azeite de Oliva',
  'Açúcar Refinado',
  'Feijão Preto',
  'Detergente Líquido',
  'Manteiga com Sal',
];

export const DespensaScreen: React.FC = () => {
  const [itens, setItens] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [categoriaAtiva, setCategoriaAtiva] = useState('Todos');
  const [busca, setBusca] = useState('');
  const [sugestoesVisiveis, setSugestoesVisiveis] = useState(false);

  // Modais
  const [modalNovoVisivel, setModalNovoVisivel] = useState(false);
  const [modalOvosVisivel, setModalOvosVisivel] = useState(false);

  // Formulário Novo Item
  const [novoNome, setNovoNome] = useState('');
  const [novoQtd, setNovoQtd] = useState('1');
  const [novoMin, setNovoMin] = useState('1');
  const [novoLocal, setNovoLocal] = useState('Armário');
  const [novoObs, setNovoObs] = useState('');

  // Controle de Ovos
  const [duziasSelecionadas, setDuziasSelecionadas] = useState(1);

  const carregarItens = async () => {
    try {
      const dados = await itensService.listar();
      setItens(dados);
    } catch (error) {
      console.error('Erro ao carregar itens:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    carregarItens();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    carregarItens();
  };

  const handleBusca = (texto: string) => {
    setBusca(texto);
    if (texto.trim().length >= 4) {
      setSugestoesVisiveis(true);
    } else {
      setSugestoesVisiveis(false);
    }
  };

  const selecionarSugestao = (sugestao: string) => {
    setBusca(sugestao);
    setSugestoesVisiveis(false);
  };

  const alterarEstoque = async (item: Item, delta: number) => {
    try {
      if (delta > 0) {
        const atualizado = await itensService.adicionarEstoque(item.id, delta);
        setItens((prev) => prev.map((i) => (i.id === item.id ? atualizado : i)));
      } else {
        if (item.quantidade <= 0) return;
        const atualizado = await itensService.removerEstoque(item.id, Math.abs(delta));
        setItens((prev) => prev.map((i) => (i.id === item.id ? atualizado : i)));
      }
    } catch (error: any) {
      Alert.alert('Erro', error.response?.data?.detail || 'Erro ao movimentar estoque.');
    }
  };

  const confirmarNovoItem = async () => {
    if (!novoNome.trim()) {
      Alert.alert('Atenção', 'Digite o nome do produto.');
      return;
    }

    try {
      const criado = await itensService.cadastrar({
        nome: novoNome.trim(),
        quantidade: parseInt(novoQtd, 10) || 0,
        quantidade_minima: parseInt(novoMin, 10) || 1,
        local: novoLocal,
        obs: novoObs.trim(),
      });
      setItens((prev) => [criado, ...prev]);
      setModalNovoVisivel(false);
      setNovoNome('');
      setNovoObs('');
      setNovoQtd('1');
    } catch (error: any) {
      Alert.alert('Erro', error.response?.data?.detail || 'Não foi possível cadastrar o item.');
    }
  };

  const confirmarEntradaOvos = async () => {
    const itemOvos = itens.find((i) => i.nome.toLowerCase().includes('ovo'));
    const ovosASomar = duziasSelecionadas * 12;

    if (itemOvos) {
      await alterarEstoque(itemOvos, ovosASomar);
      Alert.alert('Sucesso', `+${ovosASomar} ovos (${duziasSelecionadas} dz) adicionados ao estoque!`);
    } else {
      // Cria o item ovos caso não exista
      const criado = await itensService.cadastrar({
        nome: 'Ovos',
        quantidade: ovosASomar,
        quantidade_minima: 12,
        local: 'Geladeira',
        obs: 'Controle por unidades',
      });
      setItens((prev) => [criado, ...prev]);
      Alert.alert('Sucesso', `Item Ovos criado com ${ovosASomar} unidades!`);
    }
    setModalOvosVisivel(false);
  };

  // Filtragem dos itens por categoria e por busca
  const itensFiltrados = itens.filter((item) => {
    const localLimpo = (item.local || '').trim().toLowerCase();
    const catLimpa = categoriaAtiva.toLowerCase();
    const matchCategoria =
      categoriaAtiva === 'Todos' ||
      localLimpo === catLimpa ||
      (categoriaAtiva === 'Freezer' &&
        (localLimpo.includes('freezer') || localLimpo.includes('congelador')));
    const matchBusca =
      busca.trim() === '' ||
      item.nome.toLowerCase().includes(busca.toLowerCase().trim()) ||
      item.obs.toLowerCase().includes(busca.toLowerCase().trim());
    return matchCategoria && matchBusca;
  });

  const sugestoesFiltradas = SUGESTOES_CATALOGO.filter((s) =>
    s.toLowerCase().includes(busca.toLowerCase().trim())
  );

  return (
    <View style={styles.container}>
      {/* Header com Botão Contextual "+ Novo" */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerBadge}>● Despensa Compartilhada</Text>
          <Text style={styles.headerTitle}>Minha Despensa</Text>
        </View>
        <TouchableOpacity
          style={styles.btnNovo}
          onPress={() => setModalNovoVisivel(true)}
        >
          <Text style={styles.btnNovoText}>+ Novo</Text>
        </TouchableOpacity>
      </View>

      {/* Barra de Pesquisa */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Buscar produto (ex: arroz, café, leite)..."
          placeholderTextColor="#64748b"
          value={busca}
          onChangeText={handleBusca}
        />
        {busca.length > 0 && (
          <TouchableOpacity onPress={() => handleBusca('')} style={styles.btnLimparBusca}>
            <Text style={styles.btnLimparBuscaText}>✕</Text>
          </TouchableOpacity>
        )}

        {/* Dropdown de Sugestões (>= 4 caracteres) */}
        {sugestoesVisiveis && sugestoesFiltradas.length > 0 && (
          <View style={styles.dropdownSugestoes}>
            <Text style={styles.dropdownTitle}>Sugestões rápidas:</Text>
            {sugestoesFiltradas.map((sugestao) => (
              <TouchableOpacity
                key={sugestao}
                style={styles.dropdownItem}
                onPress={() => selecionarSugestao(sugestao)}
              >
                <Text style={styles.dropdownItemText}>{sugestao}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </View>

      {/* Categorias / Locais */}
      <View style={styles.categoriasContainer}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoriasList}
        >
          {CATEGORIAS.map((cat) => (
            <TouchableOpacity
              key={cat}
              style={[
                styles.categoriaBtn,
                categoriaAtiva === cat && styles.categoriaBtnAtiva,
              ]}
              onPress={() => setCategoriaAtiva(cat)}
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.categoriaText,
                  categoriaAtiva === cat && styles.categoriaTextAtiva,
                ]}
              >
                {cat}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Lista de Produtos */}
      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#10b981" />
        </View>
      ) : (
        <ScrollView
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          {itensFiltrados.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>
                {busca
                  ? 'Nenhum produto encontrado com essa busca.'
                  : 'Nenhum item nesta categoria. Toque em "+ Novo" para cadastrar!'}
              </Text>
            </View>
          ) : (
            itensFiltrados.map((item) => {
              const isOvos = item.nome.toLowerCase().includes('ovo');
              const isZerado = item.quantidade === 0;
              const isAcabando = item.quantidade <= item.quantidade_minima;

              return (
                <View
                  key={item.id}
                  style={[
                    styles.itemCard,
                    isZerado && styles.cardZerado,
                    !isZerado && isAcabando && styles.cardAcabando,
                  ]}
                >
                  <View style={styles.itemInfo}>
                    <View style={styles.itemTitleRow}>
                      <Text style={styles.itemNome}>{item.nome}</Text>
                      {isZerado && <Text style={styles.badgeZerado}>Zerado</Text>}
                      {!isZerado && isAcabando && (
                        <Text style={styles.badgeAcabando}>Acabando</Text>
                      )}
                    </View>
                    <Text style={styles.itemDetalhes}>
                      {item.local} • Mín: {item.quantidade_minima} un
                      {item.obs ? ` • OBS: ${item.obs}` : ''}
                      {isOvos ? ` • (~${(item.quantidade / 12).toFixed(1)} dz)` : ''}
                    </Text>

                    {/* Botão de Dúzias para Ovos */}
                    {isOvos && (
                      <TouchableOpacity
                        style={styles.btnDuzias}
                        onPress={() => setModalOvosVisivel(true)}
                      >
                        <Text style={styles.btnDuziasText}>+ Dúzias (dz)</Text>
                      </TouchableOpacity>
                    )}
                  </View>

                  {/* Controles de Estoque (+ e -) */}
                  <View style={styles.controlesRow}>
                    <TouchableOpacity
                      style={styles.btnAcao}
                      onPress={() => alterarEstoque(item, -1)}
                    >
                      <Text style={styles.btnAcaoText}>-</Text>
                    </TouchableOpacity>
                    <Text style={styles.qtdText}>{item.quantidade}</Text>
                    <TouchableOpacity
                      style={styles.btnAcao}
                      onPress={() => alterarEstoque(item, 1)}
                    >
                      <Text style={styles.btnAcaoText}>+</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              );
            })
          )}
        </ScrollView>
      )}

      {/* Modal 1: Novo Produto (Com Campo OBS:) */}
      <Modal visible={modalNovoVisivel} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Adicionar Novo Produto</Text>
              <TouchableOpacity onPress={() => setModalNovoVisivel(false)}>
                <Text style={styles.modalCloseText}>✕</Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.modalLabel}>Nome do Produto:</Text>
            <TextInput
              style={styles.modalInput}
              placeholder="Ex: Azeite Extra Virgem"
              placeholderTextColor="#64748b"
              value={novoNome}
              onChangeText={setNovoNome}
            />

            <View style={styles.modalRow}>
              <View style={styles.modalCol}>
                <Text style={styles.modalLabel}>Qtd Inicial:</Text>
                <TextInput
                  style={styles.modalInput}
                  keyboardType="numeric"
                  value={novoQtd}
                  onChangeText={setNovoQtd}
                />
              </View>
              <View style={styles.modalCol}>
                <Text style={styles.modalLabel}>Qtd Mínima:</Text>
                <TextInput
                  style={styles.modalInput}
                  keyboardType="numeric"
                  value={novoMin}
                  onChangeText={setNovoMin}
                />
              </View>
            </View>

            <Text style={styles.modalLabel}>Local de Armazenamento:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.localChips}>
              {CATEGORIAS.filter((c) => c !== 'Todos').map((loc) => (
                <TouchableOpacity
                  key={loc}
                  style={[
                    styles.chipBtn,
                    novoLocal === loc && styles.chipBtnAtivo,
                  ]}
                  onPress={() => setNovoLocal(loc)}
                >
                  <Text
                    style={[
                      styles.chipText,
                      novoLocal === loc && styles.chipTextAtivo,
                    ]}
                  >
                    {loc}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            {/* Campo OBS: Solicitado pelo Usuário */}
            <Text style={styles.modalLabel}>Observações (OBS):</Text>
            <TextInput
              style={styles.modalInput}
              placeholder="Ex: Marca X, Integral, Pacote 500g"
              placeholderTextColor="#64748b"
              value={novoObs}
              onChangeText={setNovoObs}
            />

            <TouchableOpacity style={styles.btnSalvarModal} onPress={confirmarNovoItem}>
              <Text style={styles.btnSalvarModalText}>Cadastrar Produto</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Modal 2: Adicionar Ovos por Dúzias */}
      <Modal visible={modalOvosVisivel} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>🥚 Entrada de Ovos</Text>
              <TouchableOpacity onPress={() => setModalOvosVisivel(false)}>
                <Text style={styles.modalCloseText}>✕</Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.modalSub}>Quantas dúzias foram compradas?</Text>

            <View style={styles.duziasGrid}>
              {[0.5, 1, 2, 3].map((dz) => (
                <TouchableOpacity
                  key={dz}
                  style={[
                    styles.dzBtn,
                    duziasSelecionadas === dz && styles.dzBtnAtivo,
                  ]}
                  onPress={() => setDuziasSelecionadas(dz)}
                >
                  <Text
                    style={[
                      styles.dzBtnText,
                      duziasSelecionadas === dz && styles.dzBtnTextAtivo,
                    ]}
                  >
                    {dz === 0.5 ? '1/2 dz' : `${dz} dz`}
                  </Text>
                  <Text style={styles.dzSubText}>({dz * 12} ovos)</Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.previewBox}>
              <Text style={styles.previewText}>Serão somados ao estoque:</Text>
              <Text style={styles.previewValor}>
                +{duziasSelecionadas * 12} unidades
              </Text>
            </View>

            <TouchableOpacity
              style={styles.btnSalvarModal}
              onPress={confirmarEntradaOvos}
            >
              <Text style={styles.btnSalvarModalText}>Confirmar e Somar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
    paddingTop: 45,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#1e293b',
  },
  headerBadge: {
    color: '#10b981',
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  headerTitle: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '800',
  },
  btnNovo: {
    backgroundColor: '#10b981',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
  },
  btnNovoText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 12,
  },
  searchContainer: {
    paddingHorizontal: 16,
    marginTop: 10,
    position: 'relative',
    zIndex: 10,
  },
  searchInput: {
    backgroundColor: '#1e293b',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#334155',
    color: '#ffffff',
    paddingHorizontal: 14,
    paddingVertical: 8,
    fontSize: 13,
  },
  btnLimparBusca: {
    position: 'absolute',
    right: 26,
    top: 9,
  },
  btnLimparBuscaText: {
    color: '#94a3b8',
    fontWeight: 'bold',
  },
  dropdownSugestoes: {
    position: 'absolute',
    top: 44,
    left: 16,
    right: 16,
    backgroundColor: '#1e293b',
    borderWidth: 1,
    borderColor: '#334155',
    borderRadius: 14,
    padding: 8,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 6,
  },
  dropdownTitle: {
    color: '#94a3b8',
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
    marginBottom: 4,
    paddingLeft: 6,
  },
  dropdownItem: {
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  dropdownItemText: {
    color: '#ffffff',
    fontSize: 12,
  },
  categoriasContainer: {
    height: 44,
    marginVertical: 4,
    justifyContent: 'center',
  },
  categoriasList: {
    paddingHorizontal: 16,
    gap: 8,
    alignItems: 'center',
  },
  categoriaBtn: {
    backgroundColor: '#1e293b',
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#334155',
    alignItems: 'center',
    justifyContent: 'center',
  },
  categoriaBtnAtiva: {
    backgroundColor: '#10b981',
    borderColor: '#10b981',
    shadowColor: '#10b981',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
  categoriaText: {
    color: '#94a3b8',
    fontSize: 12,
    fontWeight: '600',
  },
  categoriaTextAtiva: {
    color: '#ffffff',
    fontWeight: '700',
  },
  listContainer: {
    paddingHorizontal: 16,
    paddingBottom: 24,
    gap: 10,
  },
  itemCard: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 14,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#334155',
  },
  cardAcabando: {
    borderColor: '#f59e0b',
    backgroundColor: 'rgba(245, 158, 11, 0.08)',
  },
  cardZerado: {
    borderColor: '#ef4444',
    backgroundColor: 'rgba(239, 68, 68, 0.08)',
  },
  itemInfo: {
    flex: 1,
    marginRight: 10,
  },
  itemTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  itemNome: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '700',
  },
  badgeAcabando: {
    backgroundColor: 'rgba(245, 158, 11, 0.2)',
    color: '#f59e0b',
    fontSize: 9,
    fontWeight: '700',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  badgeZerado: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    color: '#ef4444',
    fontSize: 9,
    fontWeight: '700',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  itemDetalhes: {
    color: '#94a3b8',
    fontSize: 11,
    marginTop: 2,
  },
  btnDuzias: {
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    marginTop: 6,
    alignSelf: 'flex-start',
  },
  btnDuziasText: {
    color: '#10b981',
    fontSize: 10,
    fontWeight: '700',
  },
  controlesRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  btnAcao: {
    width: 30,
    height: 30,
    borderRadius: 8,
    backgroundColor: '#334155',
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnAcaoText: {
    color: '#ffffff',
    fontWeight: '800',
    fontSize: 16,
  },
  qtdText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '700',
    minWidth: 24,
    textAlign: 'center',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    padding: 30,
    alignItems: 'center',
  },
  emptyText: {
    color: '#94a3b8',
    textAlign: 'center',
    fontSize: 13,
  },
  // Estilos de Modais
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'flex-end',
  },
  modalCard: {
    backgroundColor: '#1e293b',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  modalTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '800',
  },
  modalCloseText: {
    color: '#94a3b8',
    fontSize: 16,
    fontWeight: '700',
  },
  modalSub: {
    color: '#94a3b8',
    fontSize: 12,
    marginBottom: 12,
  },
  modalLabel: {
    color: '#cbd5e1',
    fontSize: 11,
    fontWeight: '600',
    marginTop: 8,
    marginBottom: 4,
  },
  modalInput: {
    backgroundColor: '#0f172a',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
    color: '#ffffff',
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 13,
  },
  modalRow: {
    flexDirection: 'row',
    gap: 10,
  },
  modalCol: {
    flex: 1,
  },
  localChips: {
    flexDirection: 'row',
    marginVertical: 4,
  },
  chipBtn: {
    backgroundColor: '#0f172a',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
    marginRight: 6,
  },
  chipBtnAtivo: {
    backgroundColor: '#10b981',
    borderColor: '#10b981',
  },
  chipText: {
    color: '#94a3b8',
    fontSize: 11,
  },
  chipTextAtivo: {
    color: '#ffffff',
    fontWeight: '700',
  },
  btnSalvarModal: {
    backgroundColor: '#10b981',
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 18,
  },
  btnSalvarModalText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 13,
  },
  duziasGrid: {
    flexDirection: 'row',
    gap: 8,
    marginVertical: 8,
  },
  dzBtn: {
    flex: 1,
    backgroundColor: '#0f172a',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
    padding: 10,
    alignItems: 'center',
  },
  dzBtnAtivo: {
    borderColor: '#10b981',
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
  },
  dzBtnText: {
    color: '#cbd5e1',
    fontWeight: '700',
    fontSize: 12,
  },
  dzBtnTextAtivo: {
    color: '#10b981',
  },
  dzSubText: {
    color: '#64748b',
    fontSize: 9,
    marginTop: 2,
  },
  previewBox: {
    backgroundColor: '#0f172a',
    borderRadius: 12,
    padding: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  previewText: {
    color: '#94a3b8',
    fontSize: 12,
  },
  previewValor: {
    color: '#10b981',
    fontWeight: '800',
    fontSize: 14,
  },
});
