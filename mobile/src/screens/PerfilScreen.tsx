import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { authService } from '../services/api';
import { Usuario } from '../types';

interface PerfilScreenProps {
  onLogout: () => void;
}

export const PerfilScreen: React.FC<PerfilScreenProps> = ({ onLogout }) => {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    carregarUsuario();
  }, []);

  const carregarUsuario = async () => {
    try {
      const dados = await authService.me();
      setUsuario(dados);
    } catch (e) {
      console.error('Erro ao carregar usuário:', e);
    } finally {
      setLoading(false);
    }
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
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Conta da Casa</Text>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#10b981" style={{ marginTop: 40 }} />
      ) : (
        <View style={styles.content}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>M&P</Text>
          </View>

          <Text style={styles.despensaNome}>Despensa Compartilhada</Text>
          <Text style={styles.despensaSub}>
            ID da Despensa: #{usuario?.despensa_id || 1}
          </Text>

          <View style={styles.cardInfo}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Usuário:</Text>
              <Text style={styles.infoValor}>{usuario?.nome || 'Mathias'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>E-mail:</Text>
              <Text style={styles.infoValor}>{usuario?.email || 'mathias@teste.com'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Segurança:</Text>
              <Text style={[styles.infoValor, { color: '#10b981' }]}>Token JWT Criptografado</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Dispositivos:</Text>
              <Text style={styles.infoValor}>Sincronização Ativa</Text>
            </View>
          </View>

          <TouchableOpacity style={styles.btnLogout} onPress={handleLogout}>
            <Text style={styles.btnLogoutText}>Desconectar da Conta</Text>
          </TouchableOpacity>
        </View>
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
  content: {
    padding: 20,
    alignItems: 'center',
  },
  avatar: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    borderWidth: 2,
    borderColor: '#10b981',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
    marginTop: 10,
  },
  avatarText: {
    color: '#10b981',
    fontSize: 22,
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
  cardInfo: {
    backgroundColor: '#1e293b',
    borderRadius: 18,
    padding: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: '#334155',
    marginVertical: 24,
    gap: 12,
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
