import React, { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { authService } from '../services/api';

interface AuthScreenProps {
  onLoginSuccess: () => void;
}

export const AuthScreen: React.FC<AuthScreenProps> = ({ onLoginSuccess }) => {
  const [isCadastro, setIsCadastro] = useState(false);
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [nomeDespensa, setNomeDespensa] = useState('Nossa Despensa');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email.trim() || !senha.trim()) {
      Alert.alert('Atenção', 'Preencha o e-mail e a senha.');
      return;
    }

    if (isCadastro && !nome.trim()) {
      Alert.alert('Atenção', 'Preencha o seu nome para o cadastro.');
      return;
    }

    setLoading(true);
    try {
      if (isCadastro) {
        await authService.cadastro(nome.trim(), email.trim(), senha, nomeDespensa.trim());
      } else {
        await authService.login(email.trim(), senha);
      }
      onLoginSuccess();
    } catch (error: any) {
      const msg =
        error.response?.data?.detail ||
        'Não foi possível conectar. Verifique se o backend está rodando.';
      Alert.alert('Erro', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        {/* Header do App */}
        <View style={styles.header}>
          <Text style={styles.badge}>🏠 Despensa Compartilhada</Text>
          <Text style={styles.title}>Despensa Inteligente</Text>
          <Text style={styles.subtitle}>
            {isCadastro
              ? 'Crie a despensa para você e sua parceira(o)'
              : 'Acesse para gerenciar o estoque da casa'}
          </Text>
        </View>

        {/* Card do Formulário */}
        <View style={styles.card}>
          {isCadastro && (
            <>
              <Text style={styles.label}>Seu Nome:</Text>
              <TextInput
                style={styles.input}
                placeholder="Ex: Mathias"
                value={nome}
                onChangeText={setNome}
                autoCapitalize="words"
              />

              <Text style={styles.label}>Nome da Despensa (Casa):</Text>
              <TextInput
                style={styles.input}
                placeholder="Ex: Casa Mathias & Parceira"
                value={nomeDespensa}
                onChangeText={setNomeDespensa}
              />
            </>
          )}

          <Text style={styles.label}>E-mail:</Text>
          <TextInput
            style={styles.input}
            placeholder="seu@email.com"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <Text style={styles.label}>Senha:</Text>
          <TextInput
            style={styles.input}
            placeholder="••••••••"
            value={senha}
            onChangeText={setSenha}
            secureTextEntry
          />

          <TouchableOpacity
            style={styles.btnPrimary}
            onPress={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.btnPrimaryText}>
                {isCadastro ? 'Criar Conta e Despensa' : 'Entrar no Aplicativo'}
              </Text>
            )}
          </TouchableOpacity>

          {/* Toggle entre Login e Cadastro */}
          <TouchableOpacity
            style={styles.btnToggle}
            onPress={() => setIsCadastro(!isCadastro)}
          >
            <Text style={styles.btnToggleText}>
              {isCadastro
                ? 'Já possui uma conta? Faça Login'
                : 'Primeiro acesso? Crie sua Despensa'}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 28,
  },
  badge: {
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    color: '#10b981',
    fontWeight: '700',
    fontSize: 12,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 20,
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  title: {
    fontSize: 26,
    fontWeight: '800',
    color: '#ffffff',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 13,
    color: '#94a3b8',
    textAlign: 'center',
    marginTop: 6,
  },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: '#334155',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 6,
  },
  label: {
    color: '#cbd5e1',
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 6,
    marginTop: 10,
  },
  input: {
    backgroundColor: '#0f172a',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
    color: '#ffffff',
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
  },
  btnPrimary: {
    backgroundColor: '#10b981',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 22,
    shadowColor: '#10b981',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.4,
    shadowRadius: 6,
    elevation: 4,
  },
  btnPrimaryText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 14,
  },
  btnToggle: {
    marginTop: 18,
    alignItems: 'center',
  },
  btnToggleText: {
    color: '#38bdf8',
    fontSize: 13,
    fontWeight: '600',
  },
});
