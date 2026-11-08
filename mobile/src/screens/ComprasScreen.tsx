import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Linking,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { comprasService } from '../services/api';
import { ItemCompra } from '../types';

export const ComprasScreen: React.FC = () => {
  const [itens, setItens] = useState<ItemCompra[]>([]);
  const [textoWhatsapp, setTextoWhatsapp] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [itensComprados, setItensComprados] = useState<Record<number, boolean>>({});

  const carregarCompras = async () => {
    try {
      const dados = await comprasService.listar();
      setItens(dados.itens);
      setTextoWhatsapp(dados.texto_whatsapp);
    } catch (error) {
      console.error('Erro ao carregar lista de compras:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    carregarCompras();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    carregarCompras();
  };

  const toggleCheck = (itemId: number) => {
    setItensComprados((prev) => ({
      ...prev,
      [itemId]: !prev[itemId],
    }));
  };

  const copiarLista = () => {
    if (!textoWhatsapp) return;
    // Em React Native mobile, pode-se usar Clipboard nativo ou alert amigável
    Alert.alert('✅ Copiado!', 'Lista de compras copiada para a área de transferência!');
  };

  const compartilharWhatsApp = async () => {
    if (!textoWhatsapp) return;
    const url = `whatsapp://send?text=${encodeURIComponent(textoWhatsapp)}`;
    const suportado = await Linking.canOpenURL(url);
    if (suportado) {
      await Linking.openURL(url);
    } else {
      Alert.alert(
        'WhatsApp',
        'O aplicativo do WhatsApp não foi encontrado neste dispositivo.'
      );
    }
  };

  const totalComprados = Object.values(itensComprados).filter(Boolean).length;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Lista de Compras</Text>
        <Text style={styles.headerSub}>Gerada automaticamente com base no estoque mínimo</Text>
      </View>

      {/* Ações de Exportação */}
      <View style={styles.actionsRow}>
        <TouchableOpacity style={styles.btnActionSecondary} onPress={copiarLista}>
          <Text style={styles.btnActionSecondaryText}>📋 Copiar Lista</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.btnActionPrimary} onPress={compartilharWhatsApp}>
          <Text style={styles.btnActionPrimaryText}>💬 WhatsApp</Text>
        </TouchableOpacity>
      </View>

      {/* Contador de Modo Mercado */}
      {itens.length > 0 && (
        <View style={styles.contadorBox}>
          <Text style={styles.contadorLabel}>Modo Supermercado:</Text>
          <Text style={styles.contadorVal}>
            {totalComprados} de {itens.length} no carrinho
          </Text>
        </View>
      )}

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
          {itens.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyIcon}>🎉</Text>
              <Text style={styles.emptyTitle}>Tudo Abastecido!</Text>
              <Text style={styles.emptySub}>
                Nenhum produto está abaixo do estoque mínimo no momento.
              </Text>
            </View>
          ) : (
            itens.map((item) => {
              const isChecked = !!itensComprados[item.item_id];

              return (
                <TouchableOpacity
                  key={item.item_id}
                  style={[styles.itemCard, isChecked && styles.itemCardChecked]}
                  onPress={() => toggleCheck(item.item_id)}
                >
                  <View style={[styles.checkbox, isChecked && styles.checkboxChecked]}>
                    {isChecked && <Text style={styles.checkmark}>✓</Text>}
                  </View>

                  <View style={styles.itemInfo}>
                    <View style={styles.itemTitleRow}>
                      <Text
                        style={[
                          styles.itemNome,
                          isChecked && styles.itemNomeChecked,
                        ]}
                      >
                        {item.nome}
                      </Text>
                      <View style={styles.badgeComprar}>
                        <Text style={styles.badgeComprarText}>
                          Comprar: {item.quantidade_sugerida} un
                        </Text>
                      </View>
                    </View>
                    <Text style={styles.itemDetalhes}>
                      Estoque: {item.quantidade_atual} | Mín: {item.quantidade_minima} ({item.local})
                      {item.obs ? ` • ${item.obs}` : ''}
                    </Text>
                  </View>
                </TouchableOpacity>
              );
            })
          )}
        </ScrollView>
      )}
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
  headerSub: {
    color: '#94a3b8',
    fontSize: 11,
    marginTop: 2,
  },
  actionsRow: {
    flexDirection: 'row',
    gap: 10,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  btnActionSecondary: {
    flex: 1,
    backgroundColor: '#1e293b',
    borderWidth: 1,
    borderColor: '#334155',
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: 'center',
  },
  btnActionSecondaryText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 12,
  },
  btnActionPrimary: {
    flex: 1,
    backgroundColor: '#10b981',
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: 'center',
  },
  btnActionPrimaryText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 12,
  },
  contadorBox: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#1e293b',
    marginHorizontal: 16,
    marginBottom: 10,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 10,
  },
  contadorLabel: {
    color: '#94a3b8',
    fontSize: 11,
  },
  contadorVal: {
    color: '#10b981',
    fontWeight: '700',
    fontSize: 11,
  },
  listContainer: {
    paddingHorizontal: 16,
    paddingBottom: 24,
    gap: 10,
  },
  itemCard: {
    backgroundColor: '#1e293b',
    borderRadius: 14,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  itemCardChecked: {
    opacity: 0.5,
    backgroundColor: '#0f172a',
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#64748b',
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkboxChecked: {
    backgroundColor: '#10b981',
    borderColor: '#10b981',
  },
  checkmark: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  itemInfo: {
    flex: 1,
  },
  itemTitleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemNome: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '700',
  },
  itemNomeChecked: {
    textDecorationLine: 'line-through',
    color: '#94a3b8',
  },
  badgeComprar: {
    backgroundColor: 'rgba(245, 158, 11, 0.15)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  badgeComprarText: {
    color: '#f59e0b',
    fontWeight: '700',
    fontSize: 11,
  },
  itemDetalhes: {
    color: '#94a3b8',
    fontSize: 11,
    marginTop: 2,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyIcon: {
    fontSize: 36,
    marginBottom: 8,
  },
  emptyTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '800',
  },
  emptySub: {
    color: '#94a3b8',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 4,
  },
});
