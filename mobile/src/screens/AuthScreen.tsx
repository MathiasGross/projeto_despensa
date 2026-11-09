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
import { API_URL, authService } from '../services/api';

interface AuthScreenProps {
  onLoginSuccess: () => void;
}

export const AuthScreen: React.FC<AuthScreenProps> = ({ onLoginSuccess }) => {
  const [modo, setModo] = useState<'login' | 'cadastro' | 'otp'>('login');
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [nomeDespensa, setNomeDespensa] = useState('Nossa Despensa');
  const [codigoOtp, setCodigoOtp] = useState('');
  const [codigoDev, setCodigoDev] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email.trim()) {
      Alert.alert('Atenção', 'Informe o seu e-mail.');
      return;
    }

    if (modo === 'otp') {
      if (!codigoOtp.trim() || codigoOtp.trim().length < 4) {
        Alert.alert('Atenção', 'Digite o código de verificação recebido.');
        return;
      }

      setLoading(true);
      try {
        await authService.verificarCodigo(email.trim(), codigoOtp.trim());
        Alert.alert('Sucesso!', 'Conta verificada com sucesso! Bem-vindo(a).');
        onLoginSuccess();
      } catch (error: any) {
        const msg =
          error.response?.data?.detail ||
          'Código inválido ou expirado. Tente novamente.';
        Alert.alert('Erro na Verificação', msg);
      } finally {
        setLoading(false);
      }
      return;
    }

    if (!senha.trim()) {
      Alert.alert('Atenção', 'Digite a sua senha.');
      return;
    }

    if (modo === 'cadastro' && !nome.trim()) {
      Alert.alert('Atenção', 'Preencha o seu nome para o cadastro.');
      return;
    }

    setLoading(true);
    try {
      if (modo === 'cadastro') {
        const res = await authService.cadastro(
          nome.trim(),
          email.trim(),
          senha,
          nomeDespensa.trim()
        );
        if (res?.codigo_dev) {
          setCodigoDev(res.codigo_dev);
          setCodigoOtp(res.codigo_dev);
        }
        Alert.alert(
          'Código Enviado!',
          'Enviamos um código de 6 dígitos para o seu e-mail. Digite-o para concluir a ativação.'
        );
        setModo('otp');
      } else {
        await authService.login(email.trim(), senha);
        onLoginSuccess();
      }
    } catch (error: any) {
      if (error.response?.status === 403) {
        // Conta pendente de validação
        Alert.alert(
          'Validação Pendente',
          'Sua conta ainda não foi verificada. Enviamos um novo código para seu e-mail.'
        );
        setModo('otp');
      } else {
        const msg =
          error.response?.data?.detail ||
          (error.message?.includes('Network Error')
            ? `Não foi possível conectar ao servidor em ${API_URL}.\n\nVerifique se o backend está ligado e se o celular e o computador estão na mesma rede Wi-Fi.`
            : error.message || 'Verifique seus dados e tente novamente.');
        Alert.alert('Erro de Conexão', msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReenviarCodigo = async () => {
    if (!email.trim()) {
      Alert.alert('Atenção', 'Digite seu e-mail para reenviar o código.');
      return;
    }
    setLoading(true);
    try {
      const res = await authService.reenviarCodigo(email.trim());
      if (res?.codigo_dev) {
        setCodigoDev(res.codigo_dev);
        setCodigoOtp(res.codigo_dev);
      }
      Alert.alert('Código Reenviado', 'Verifique a sua caixa de entrada e spam.');
    } catch (error: any) {
      Alert.alert(
        'Erro',
        error.response?.data?.detail || 'Erro ao reenviar código.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleLoginGoogle = async () => {
    setLoading(true);
    try {
      // Token demonstrativo para desenvolvimento e testes
      const mockToken = `mock-google-token:${email.trim() || 'usuario.google@gmail.com'}:${nome.trim() || 'Usuário Google'}:google-uid-${Date.now()}`;
      await authService.loginGoogle(mockToken, nomeDespensa.trim());
      Alert.alert('Google Auth', 'Login realizado com o Google com sucesso!');
      onLoginSuccess();
    } catch (error: any) {
      const msg =
        error.response?.data?.detail ||
        (error.message?.includes('Network Error')
          ? `Não foi possível conectar ao servidor em ${API_URL}.\n\nVerifique se o backend está ligado e se o celular e o computador estão no mesmo Wi-Fi.`
          : 'Falha ao autenticar com o Google.');
      Alert.alert('Erro no Google', msg);
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
            {modo === 'otp'
              ? 'Validação de Segurança por Código Único'
              : modo === 'cadastro'
              ? 'Crie sua conta e despensa para o casal/família'
              : 'Acesse para gerenciar o estoque da casa'}
          </Text>
        </View>

        {/* Card do Formulário */}
        <View style={styles.card}>
          {modo === 'otp' ? (
            <>
              <View style={styles.otpHeader}>
                <Text style={styles.otpIcon}>✉️</Text>
                <Text style={styles.otpTitle}>Verifique seu E-mail</Text>
                <Text style={styles.otpSub}>
                  Digitamos o código de 6 dígitos enviado para{' '}
                  <Text style={{ fontWeight: 'bold', color: '#10b981' }}>{email}</Text>
                </Text>
              </View>

              {codigoDev && (
                <TouchableOpacity
                  style={styles.cardCodigoDev}
                  onPress={() => setCodigoOtp(codigoDev)}
                >
                  <Text style={styles.cardCodigoDevTitulo}>⚡ Código para Teste Rápido:</Text>
                  <Text style={styles.cardCodigoDevCode}>{codigoDev}</Text>
                  <Text style={styles.cardCodigoDevSub}>Toque aqui para preencher automaticamente</Text>
                </TouchableOpacity>
              )}

              <Text style={styles.label}>Código de Verificação (6 dígitos):</Text>
              <TextInput
                style={[styles.input, styles.otpInput]}
                placeholder="123456"
                placeholderTextColor="#64748b"
                value={codigoOtp}
                onChangeText={setCodigoOtp}
                keyboardType="numeric"
                maxLength={6}
                autoFocus
              />

              <TouchableOpacity
                style={styles.btnPrimary}
                onPress={handleSubmit}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.btnPrimaryText}>Validar Código e Entrar</Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.btnSecundario}
                onPress={handleReenviarCodigo}
                disabled={loading}
              >
                <Text style={styles.btnSecundarioText}>🔄 Reenviar novo código</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.btnToggle}
                onPress={() => setModo('login')}
              >
                <Text style={styles.btnToggleText}>← Voltar para o Login</Text>
              </TouchableOpacity>
            </>
          ) : (
            <>
              {modo === 'cadastro' && (
                <>
                  <Text style={styles.label}>Seu Nome:</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="Ex: Mathias"
                    placeholderTextColor="#64748b"
                    value={nome}
                    onChangeText={setNome}
                    autoCapitalize="words"
                  />

                  <Text style={styles.label}>Nome da Despensa (Casa):</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="Ex: Casa Mathias & Parceira"
                    placeholderTextColor="#64748b"
                    value={nomeDespensa}
                    onChangeText={setNomeDespensa}
                  />
                </>
              )}

              <Text style={styles.label}>E-mail:</Text>
              <TextInput
                style={styles.input}
                placeholder="seu@email.com"
                placeholderTextColor="#64748b"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />

              <Text style={styles.label}>Senha:</Text>
              <TextInput
                style={styles.input}
                placeholder="••••••••"
                placeholderTextColor="#64748b"
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
                    {modo === 'cadastro'
                      ? 'Cadastrar e Receber Código'
                      : 'Entrar no Aplicativo'}
                  </Text>
                )}
              </TouchableOpacity>

              {/* Botão de Login com o Google */}
              <View style={styles.divisor}>
                <View style={styles.linhaDivisora} />
                <Text style={styles.divisorTexto}>OU ACESSE COM</Text>
                <View style={styles.linhaDivisora} />
              </View>

              <TouchableOpacity
                style={styles.btnGoogle}
                onPress={handleLoginGoogle}
                disabled={loading}
              >
                <Text style={styles.btnGoogleIcon}>🌐</Text>
                <Text style={styles.btnGoogleText}>Continuar com o Google</Text>
              </TouchableOpacity>

              {/* Toggle entre Login e Cadastro */}
              <TouchableOpacity
                style={styles.btnToggle}
                onPress={() =>
                  setModo(modo === 'cadastro' ? 'login' : 'cadastro')
                }
              >
                <Text style={styles.btnToggleText}>
                  {modo === 'cadastro'
                    ? 'Já possui uma conta? Faça Login'
                    : 'Primeiro acesso? Crie sua Despensa'}
                </Text>
              </TouchableOpacity>
            </>
          )}
        </View>

        {/* Indicador do Servidor Conectado */}
        <View style={styles.serverInfoBox}>
          <Text style={styles.serverInfoText}>
            📡 Servidor API: <Text style={{ color: '#10b981', fontWeight: 'bold' }}>{API_URL}</Text>
          </Text>
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
    marginBottom: 24,
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
  otpHeader: {
    alignItems: 'center',
    marginBottom: 16,
  },
  otpIcon: {
    fontSize: 40,
    marginBottom: 8,
  },
  otpTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#ffffff',
  },
  otpSub: {
    fontSize: 13,
    color: '#94a3b8',
    textAlign: 'center',
    marginTop: 6,
    lineHeight: 18,
  },
  cardCodigoDev: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#10b981',
    padding: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  cardCodigoDevTitulo: {
    color: '#10b981',
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  cardCodigoDevCode: {
    color: '#ffffff',
    fontSize: 24,
    fontWeight: '800',
    letterSpacing: 6,
    marginVertical: 4,
  },
  cardCodigoDevSub: {
    color: '#34d399',
    fontSize: 11,
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
  otpInput: {
    textAlign: 'center',
    fontSize: 26,
    fontWeight: '800',
    letterSpacing: 10,
    color: '#10b981',
    borderColor: '#10b981',
    backgroundColor: 'rgba(16, 185, 129, 0.05)',
  },
  btnPrimary: {
    backgroundColor: '#10b981',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 20,
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
  btnSecundario: {
    backgroundColor: 'rgba(56, 189, 248, 0.1)',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 12,
    borderWidth: 1,
    borderColor: 'rgba(56, 189, 248, 0.3)',
  },
  btnSecundarioText: {
    color: '#38bdf8',
    fontSize: 13,
    fontWeight: '600',
  },
  divisor: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 18,
  },
  linhaDivisora: {
    flex: 1,
    height: 1,
    backgroundColor: '#334155',
  },
  divisorTexto: {
    color: '#64748b',
    fontSize: 10,
    fontWeight: '700',
    paddingHorizontal: 10,
    letterSpacing: 1,
  },
  btnGoogle: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 14,
    paddingVertical: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
    elevation: 3,
  },
  btnGoogleIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  btnGoogleText: {
    color: '#0f172a',
    fontSize: 14,
    fontWeight: '700',
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
  serverInfoBox: {
    marginTop: 16,
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
  },
  serverInfoText: {
    color: '#94a3b8',
    fontSize: 11,
  },
});
