from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import secrets
import smtplib

logger = logging.getLogger("email_service")

# Armazena em memória os últimos códigos gerados (útil para testes automáticos e ambiente local dev)
ULTIMOS_CODIGOS_DEV: dict[str, str] = {}


def gerar_codigo_otp(tamanho: int = 6) -> str:
    """Gera um código OTP numérico aleatório de 6 dígitos."""
    return "".join(secrets.choice("0123456789") for _ in range(tamanho))


def enviar_email_codigo(destinatario: str, nome: str, codigo: str) -> bool:
    """
    Envia o código de 6 dígitos para o e-mail do usuário.
    Se as credenciais SMTP estiverem configuradas no ambiente, envia via SMTP real.
    Caso contrário, registra em modo DEV (com mock transparente para desenvolvimento e testes).
    """
    email_limpo = destinatario.strip().lower()
    ULTIMOS_CODIGOS_DEV[email_limpo] = codigo

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    remetente = os.getenv("SMTP_FROM", "despensa@suaempresa.com")

    if not smtp_host or not smtp_user or not smtp_pass:
        # Modo de desenvolvimento/testes
        logger.info(
            f"[MODO DEV] Código de verificação para {email_limpo} ({nome}): {codigo}"
        )
        print(
            f" [CÓDIGO OTP DEV] E-mail: {email_limpo} | Código de 6 dígitos: {codigo} "
        )
        return True

    # Envio real via SMTP
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{codigo} é o seu código de acesso - Despensa Doméstica"
        msg["From"] = remetente
        msg["To"] = email_limpo

        texto_plano = f"""Olá, {nome}!

Seu código de confirmação para a Despensa Inteligente é:

{codigo}

Este código é válido por 15 minutos. Não compartilhe com ninguém.
Se você não solicitou este cadastro, desconsidere esta mensagem.
"""

        texto_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #16a34a; margin: 0;">🧺 Despensa Doméstica</h2>
                <p style="color: #64748b; font-size: 14px;">Controle inteligente de despensa e lista de compras</p>
            </div>
            <p style="color: #334155; font-size: 16px;">Olá, <strong>{nome}</strong>!</p>
            <p style="color: #475569; font-size: 14px; line-height: 1.5;">
                Recebemos seu pedido de cadastro. Utilize o código de 6 dígitos abaixo para concluir sua ativação:
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #16a34a; background-color: #f0fdf4; padding: 12px 24px; border-radius: 8px; border: 1px dashed #22c55e;">
                    {codigo}
                </span>
            </div>
            <p style="color: #64748b; font-size: 12px; text-align: center;">
                Este código expira em <strong>15 minutos</strong>. Não o compartilhe com ninguém.
            </p>
        </div>
        """

        msg.attach(MIMEText(texto_plano, "plain"))
        msg.attach(MIMEText(texto_html, "html"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(remetente, [email_limpo], msg.as_string())

        return True
    except Exception as exc:
        logger.error(f"Erro ao enviar e-mail via SMTP para {email_limpo}: {exc}")
        return False
