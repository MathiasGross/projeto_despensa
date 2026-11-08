import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import {
  ActivityIndicator,
  SafeAreaView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { authService } from './src/services/api';
import { AuthScreen } from './src/screens/AuthScreen';
import { DespensaScreen } from './src/screens/DespensaScreen';
import { ComprasScreen } from './src/screens/ComprasScreen';
import { ChefScreen } from './src/screens/ChefScreen';
import { PerfilScreen } from './src/screens/PerfilScreen';

type AbaAtiva = 'despensa' | 'compras' | 'chef' | 'perfil';

export default function App() {
  const [autenticado, setAutenticado] = useState(false);
  const [loading, setLoading] = useState(true);
  const [abaAtiva, setAbaAtiva] = useState<AbaAtiva>('despensa');

  useEffect(() => {
    verificarSessao();
  }, []);

  const verificarSessao = async () => {
    try {
      const token = await authService.obterToken();
      if (token) {
        setAutenticado(true);
      }
    } catch (e) {
      console.error('Erro ao verificar sessão:', e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#10b981" />
      </View>
    );
  }

  if (!autenticado) {
    return (
      <>
        <StatusBar style="light" />
        <AuthScreen onLoginSuccess={() => setAutenticado(true)} />
      </>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />

      {/* Conteúdo da Tela Ativa */}
      <View style={styles.content}>
        {abaAtiva === 'despensa' && <DespensaScreen />}
        {abaAtiva === 'compras' && <ComprasScreen />}
        {abaAtiva === 'chef' && <ChefScreen />}
        {abaAtiva === 'perfil' && (
          <PerfilScreen onLogout={() => setAutenticado(false)} />
        )}
      </View>

      {/* Barra de Navegação Inferior (Bottom Tabs) */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setAbaAtiva('despensa')}
        >
          <Text
            style={[
              styles.navIcon,
              abaAtiva === 'despensa' && styles.navIconAtivo,
            ]}
          >
            📦
          </Text>
          <Text
            style={[
              styles.navText,
              abaAtiva === 'despensa' && styles.navTextAtivo,
            ]}
          >
            Despensa
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setAbaAtiva('compras')}
        >
          <Text
            style={[
              styles.navIcon,
              abaAtiva === 'compras' && styles.navIconAtivo,
            ]}
          >
            🛒
          </Text>
          <Text
            style={[
              styles.navText,
              abaAtiva === 'compras' && styles.navTextAtivo,
            ]}
          >
            Compras
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setAbaAtiva('chef')}
        >
          <Text
            style={[
              styles.navIcon,
              abaAtiva === 'chef' && styles.navIconAtivo,
            ]}
          >
            👨‍🍳
          </Text>
          <Text
            style={[
              styles.navText,
              abaAtiva === 'chef' && styles.navTextAtivo,
            ]}
          >
            Chef IA
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navItem}
          onPress={() => setAbaAtiva('perfil')}
        >
          <Text
            style={[
              styles.navIcon,
              abaAtiva === 'perfil' && styles.navIconAtivo,
            ]}
          >
            👤
          </Text>
          <Text
            style={[
              styles.navText,
              abaAtiva === 'perfil' && styles.navTextAtivo,
            ]}
          >
            Perfil
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#0f172a',
    alignItems: 'center',
    justifyContent: 'center',
  },
  content: {
    flex: 1,
  },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: '#1e293b',
    borderTopWidth: 1,
    borderTopColor: '#334155',
    paddingVertical: 8,
    paddingBottom: 16,
  },
  navItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  navIcon: {
    fontSize: 20,
    marginBottom: 2,
    opacity: 0.5,
  },
  navIconAtivo: {
    opacity: 1,
  },
  navText: {
    color: '#94a3b8',
    fontSize: 10,
    fontWeight: '700',
  },
  navTextAtivo: {
    color: '#10b981',
  },
});
