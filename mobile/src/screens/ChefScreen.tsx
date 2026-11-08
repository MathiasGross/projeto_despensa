import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { aiService, itensService } from '../services/api';
import { Item, Receita } from '../types';

export const ChefScreen: React.FC = () => {
  const [tipo, setTipo] = useState<'salgado' | 'doce'>('salgado');
  const [subTipo, setSubTipo] = useState<string>('principal');
  const [modo, setModo] = useState<'base' | 'random'>('base');

  const [itensEstoque, setItensEstoque] = useState<Item[]>([]);
  const [produtosSelecionados, setProdutosSelecionados] = useState<string[]>(['Ovos', 'Arroz']);
  const [modalProdutosVisivel, setModalProdutosVisivel] = useState(false);

  const [receita, setReceita] = useState<Receita | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    carregarEstoque();
  }, []);

  const carregarEstoque = async () => {
    try {
      const dados = await itensService.listar();
      setItensEstoque(dados.filter((i) => i.quantidade > 0));
    } catch (e) {
      console.error('Erro ao carregar itens para o chef:', e);
    }
  };

  const alternarTipo = (novoTipo: 'salgado' | 'doce') => {
    setTipo(novoTipo);
    setSubTipo(novoTipo === 'salgado' ? 'principal' : 'sobremesa');
  };

  const toggleProdutoModal = (nome: string) => {
    setProdutosSelecionados((prev) =>
      prev.includes(nome) ? prev.filter((p) => p !== nome) : [...prev, nome]
    );
  };

  const removerProduto = (nome: string) => {
    setProdutosSelecionados((prev) => prev.filter((p) => p !== nome));
  };

  const gerarReceita = async () => {
    setLoading(true);
    try {
      const resposta = await aiService.sugerirReceitas();
      if (resposta.receitas && resposta.receitas.length > 0) {
        setReceita(resposta.receitas[0]);
      } else {
        Alert.alert('Atenção', resposta.mensagem || 'Nenhuma receita gerada.');
      }
    } catch (error: any) {
      Alert.alert('Erro', 'Não foi possível consultar o Chef IA.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      {/* Banner Chef IA com Chapéu de Chef */}
      <View style={styles.banner}>
        <View style={styles.hatIconContainer}>
          <Text style={styles.hatEmoji}>👨‍🍳</Text>
        </View>
        <Text style={styles.bannerTitle}>Chef Inteligente Gemini</Text>
        <Text style={styles.bannerSub}>
          Crie receitas culinárias sob medida com o estoque da sua casa.
        </Text>
      </View>

      {/* Seletor 1: Salgado vs Doce */}
      <View style={styles.tipoContainer}>
        <TouchableOpacity
          style={[styles.tipoBtn, tipo === 'salgado' && styles.tipoBtnAtivoSalgado]}
          onPress={() => alternarTipo('salgado')}
        >
          <Text
            style={[
              styles.tipoBtnText,
              tipo === 'salgado' && styles.tipoBtnTextAtivoSalgado,
            ]}
          >
            🧂 Salgado
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tipoBtn, tipo === 'doce' && styles.tipoBtnAtivoDoce]}
          onPress={() => alternarTipo('doce')}
        >
          <Text
            style={[
              styles.tipoBtnText,
              tipo === 'doce' && styles.tipoBtnTextAtivoDoce,
            ]}
          >
            🍰 Doce
          </Text>
        </TouchableOpacity>
      </View>

      {/* Seletor 2: Sub-ocasião */}
      <View style={styles.sectionCard}>
        <Text style={styles.sectionLabel}>Ocasião da Receita:</Text>
        <View style={styles.subGrid}>
          {tipo === 'salgado' ? (
            <>
              <TouchableOpacity
                style={[
                  styles.subBtn,
                  subTipo === 'principal' && styles.subBtnAtivoSalgado,
                ]}
                onPress={() => setSubTipo('principal')}
              >
                <Text style={styles.subBtnTitle}>🍽️ Refeição Principal</Text>
                <Text style={styles.subBtnDesc}>Almoço ou Jantar</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.subBtn,
                  subTipo === 'lanche' && styles.subBtnAtivoSalgado,
                ]}
                onPress={() => setSubTipo('lanche')}
              >
                <Text style={styles.subBtnTitle}>🥪 Lanche Rápido</Text>
                <Text style={styles.subBtnDesc}>Snack em 10 min</Text>
              </TouchableOpacity>
            </>
          ) : (
            <>
              <TouchableOpacity
                style={[
                  styles.subBtn,
                  subTipo === 'sobremesa' && styles.subBtnAtivoDoce,
                ]}
                onPress={() => setSubTipo('sobremesa')}
              >
                <Text style={styles.subBtnTitle}>🍨 Sobremesa</Text>
                <Text style={styles.subBtnDesc}>Prato doce completo</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.subBtn,
                  subTipo === 'doce-rapido' && styles.subBtnAtivoDoce,
                ]}
                onPress={() => setSubTipo('doce-rapido')}
              >
                <Text style={styles.subBtnTitle}>🍪 Doce Rápido</Text>
                <Text style={styles.subBtnDesc}>Caneca / Individual</Text>
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>

      {/* Seletor 3: Modo de Ingredientes */}
      <View style={styles.sectionCard}>
        <View style={styles.modoHeader}>
          <Text style={styles.sectionLabel}>Como deseja escolher?</Text>
          <View style={styles.modoToggle}>
            <TouchableOpacity
              style={[styles.modoBtn, modo === 'base' && styles.modoBtnAtivo]}
              onPress={() => setModo('base')}
            >
              <Text
                style={[
                  styles.modoBtnText,
                  modo === 'base' && styles.modoBtnTextAtivo,
                ]}
              >
                Escolher Produtos
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.modoBtn, modo === 'random' && styles.modoBtnAtivoRandom]}
              onPress={() => setModo('random')}
            >
              <Text
                style={[
                  styles.modoBtnText,
                  modo === 'random' && styles.modoBtnTextAtivo,
                ]}
              >
                🎲 Aleatória
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {modo === 'base' ? (
          <View style={styles.baseContainer}>
            <Text style={styles.baseInstrucao}>
              Toque para selecionar os ingredientes obrigatórios para gerar receita:
            </Text>

            {/* Botão de Destaque "+ Adicionar Produtos da Despensa" */}
            <TouchableOpacity
              style={styles.btnAddProdutos}
              onPress={() => setModalProdutosVisivel(true)}
            >
              <Text style={styles.btnAddProdutosText}>
                + Adicionar Produtos da Despensa
              </Text>
            </TouchableOpacity>

            {/* Chips Selecionados */}
            <View style={styles.chipsRow}>
              {produtosSelecionados.map((prod) => (
                <View key={prod} style={styles.chip}>
                  <Text style={styles.chipText}>{prod}</Text>
                  <TouchableOpacity onPress={() => removerProduto(prod)}>
                    <Text style={styles.chipClose}>✕</Text>
                  </TouchableOpacity>
                </View>
              ))}
              {produtosSelecionados.length === 0 && (
                <Text style={styles.emptyChipsText}>
                  Nenhum produto selecionado. Toque no botão acima para adicionar.
                </Text>
              )}
            </View>
          </View>
        ) : (
          <View style={styles.randomBox}>
            <Text style={styles.randomText}>
              🎲 O Chef IA escolherá os ingredientes da sua despensa de forma livre e criativa!
            </Text>
          </View>
        )}
      </View>

      {/* Botão Principal de Geração de Receita */}
      <TouchableOpacity
        style={styles.btnGerar}
        onPress={gerarReceita}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnGerarText}>👨‍🍳 Gerar Receita com o Chef IA</Text>
        )}
      </TouchableOpacity>

      {/* Card da Receita Gerada */}
      {receita && (
        <View style={styles.receitaCard}>
          <View style={styles.receitaHeader}>
            <View style={styles.badgeReceita}>
              <Text style={styles.badgeReceitaText}>
                {tipo === 'salgado' ? 'Salgado' : 'Doce'} • {subTipo}
              </Text>
            </View>
            <Text style={styles.tempoReceita}>⏱️ {receita.tempo_minutos} min</Text>
          </View>

          <Text style={styles.receitaTitulo}>{receita.titulo}</Text>
          <Text style={styles.receitaDescricao}>{receita.descricao}</Text>

          <View style={styles.ingredientesBox}>
            <Text style={styles.boxTitle}>Ingredientes Utilizados:</Text>
            {receita.ingredientes.map((ing, idx) => (
              <Text key={idx} style={styles.ingredienteItem}>
                {ing.disponivel_em_casa ? '✓' : '+'} {ing.nome} ({ing.quantidade_estimada})
              </Text>
            ))}
          </View>

          <View style={styles.passosBox}>
            <Text style={styles.boxTitle}>Modo de Preparo:</Text>
            {receita.passo_a_passo.map((passo, idx) => (
              <Text key={idx} style={styles.passoItem}>
                {idx + 1}. {passo}
              </Text>
            ))}
          </View>
        </View>
      )}

      {/* Modal de Escolha de Produtos da Despensa */}
      <Modal visible={modalProdutosVisivel} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Selecione Produtos da Despensa</Text>
              <TouchableOpacity onPress={() => setModalProdutosVisivel(false)}>
                <Text style={styles.modalCloseText}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalScroll}>
              {itensEstoque.length === 0 ? (
                <Text style={styles.modalEmpty}>Nenhum produto com estoque disponível.</Text>
              ) : (
                itensEstoque.map((item) => {
                  const isChecked = produtosSelecionados.includes(item.nome);
                  return (
                    <TouchableOpacity
                      key={item.id}
                      style={[
                        styles.itemModalRow,
                        isChecked && styles.itemModalRowChecked,
                      ]}
                      onPress={() => toggleProdutoModal(item.nome)}
                    >
                      <Text style={styles.itemModalNome}>
                        {item.nome} ({item.quantidade} un)
                      </Text>
                      <Text style={styles.checkIcon}>{isChecked ? '☑' : '☐'}</Text>
                    </TouchableOpacity>
                  );
                })
              )}
            </ScrollView>

            <TouchableOpacity
              style={styles.btnConfirmarModal}
              onPress={() => setModalProdutosVisivel(false)}
            >
              <Text style={styles.btnConfirmarModalText}>Confirmar Seleção</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
    paddingTop: 45,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 30,
    gap: 12,
  },
  banner: {
    backgroundColor: 'rgba(16, 185, 129, 0.08)',
    borderRadius: 20,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.2)',
  },
  hatIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 14,
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 6,
  },
  hatEmoji: {
    fontSize: 24,
  },
  bannerTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '800',
  },
  bannerSub: {
    color: '#94a3b8',
    fontSize: 11,
    textAlign: 'center',
    marginTop: 2,
  },
  tipoContainer: {
    flexDirection: 'row',
    backgroundColor: '#1e293b',
    borderRadius: 14,
    padding: 4,
    gap: 4,
  },
  tipoBtn: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 10,
  },
  tipoBtnAtivoSalgado: {
    backgroundColor: '#0f172a',
    borderWidth: 1,
    borderColor: '#10b981',
  },
  tipoBtnAtivoDoce: {
    backgroundColor: '#0f172a',
    borderWidth: 1,
    borderColor: '#ec4899',
  },
  tipoBtnText: {
    color: '#94a3b8',
    fontWeight: '700',
    fontSize: 13,
  },
  tipoBtnTextAtivoSalgado: {
    color: '#10b981',
  },
  tipoBtnTextAtivoDoce: {
    color: '#ec4899',
  },
  sectionCard: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: '#334155',
  },
  sectionLabel: {
    color: '#94a3b8',
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  subGrid: {
    flexDirection: 'row',
    gap: 8,
  },
  subBtn: {
    flex: 1,
    backgroundColor: '#0f172a',
    borderRadius: 12,
    padding: 10,
    borderWidth: 1,
    borderColor: '#334155',
  },
  subBtnAtivoSalgado: {
    borderColor: '#10b981',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
  },
  subBtnAtivoDoce: {
    borderColor: '#ec4899',
    backgroundColor: 'rgba(236, 72, 153, 0.1)',
  },
  subBtnTitle: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
  },
  subBtnDesc: {
    color: '#64748b',
    fontSize: 10,
    marginTop: 2,
  },
  modoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  modoToggle: {
    flexDirection: 'row',
    gap: 4,
  },
  modoBtn: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  modoBtnAtivo: {
    backgroundColor: '#0f172a',
    borderWidth: 1,
    borderColor: '#10b981',
  },
  modoBtnAtivoRandom: {
    backgroundColor: '#9333ea',
  },
  modoBtnText: {
    color: '#94a3b8',
    fontSize: 11,
    fontWeight: '600',
  },
  modoBtnTextAtivo: {
    color: '#ffffff',
  },
  baseContainer: {
    marginTop: 6,
  },
  baseInstrucao: {
    color: '#94a3b8',
    fontSize: 10,
    marginBottom: 8,
  },
  btnAddProdutos: {
    borderWidth: 1.5,
    borderStyle: 'dashed',
    borderColor: '#10b981',
    backgroundColor: 'rgba(16, 185, 129, 0.08)',
    borderRadius: 12,
    paddingVertical: 10,
    alignItems: 'center',
  },
  btnAddProdutosText: {
    color: '#10b981',
    fontSize: 12,
    fontWeight: '700',
  },
  chipsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 8,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    borderWidth: 1,
    borderColor: '#10b981',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
    gap: 6,
  },
  chipText: {
    color: '#10b981',
    fontSize: 12,
    fontWeight: '600',
  },
  chipClose: {
    color: '#ef4444',
    fontSize: 11,
    fontWeight: 'bold',
  },
  emptyChipsText: {
    color: '#64748b',
    fontSize: 11,
    fontStyle: 'italic',
  },
  randomBox: {
    backgroundColor: 'rgba(147, 51, 234, 0.1)',
    borderRadius: 10,
    padding: 10,
    borderWidth: 1,
    borderColor: 'rgba(147, 51, 234, 0.2)',
  },
  randomText: {
    color: '#c084fc',
    fontSize: 11,
  },
  btnGerar: {
    backgroundColor: '#10b981',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
    shadowColor: '#10b981',
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  btnGerarText: {
    color: '#ffffff',
    fontWeight: '800',
    fontSize: 14,
  },
  receitaCard: {
    backgroundColor: '#1e293b',
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: '#334155',
    gap: 10,
  },
  receitaHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  badgeReceita: {
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
  },
  badgeReceitaText: {
    color: '#10b981',
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  tempoReceita: {
    color: '#94a3b8',
    fontSize: 12,
    fontWeight: '600',
  },
  receitaTitulo: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '800',
  },
  receitaDescricao: {
    color: '#94a3b8',
    fontSize: 12,
  },
  ingredientesBox: {
    backgroundColor: '#0f172a',
    borderRadius: 12,
    padding: 10,
  },
  boxTitle: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '700',
    marginBottom: 6,
    textTransform: 'uppercase',
  },
  ingredienteItem: {
    color: '#cbd5e1',
    fontSize: 12,
    marginVertical: 2,
  },
  passosBox: {
    marginTop: 4,
  },
  passoItem: {
    color: '#e2e8f0',
    fontSize: 12,
    marginVertical: 4,
    lineHeight: 18,
  },
  // Modal
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
    maxHeight: '70%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  modalTitle: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '700',
  },
  modalCloseText: {
    color: '#94a3b8',
    fontSize: 16,
    fontWeight: 'bold',
  },
  modalScroll: {
    marginVertical: 10,
  },
  modalEmpty: {
    color: '#94a3b8',
    fontSize: 12,
    textAlign: 'center',
    padding: 20,
  },
  itemModalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#0f172a',
    padding: 12,
    borderRadius: 10,
    marginBottom: 6,
  },
  itemModalRowChecked: {
    borderColor: '#10b981',
    borderWidth: 1,
  },
  itemModalNome: {
    color: '#ffffff',
    fontSize: 13,
  },
  checkIcon: {
    color: '#10b981',
    fontSize: 16,
  },
  btnConfirmarModal: {
    backgroundColor: '#10b981',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  btnConfirmarModalText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 13,
  },
});
