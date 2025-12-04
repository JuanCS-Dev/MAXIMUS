# Checklist de Manutenção - Janeiro 2025

## Diagnóstico Atual (03/12/2024)
- **RAM**: 16GB (OK)
- **Disco**: 234GB SSD NVMe
- **SO**: Linux Mint
- **Problema**: 34+ processos Chrome/Chromium consumindo recursos

## Limpeza Realizada (03/12)
- ✅ 18.6GB de cache liberados
- ✅ Disco: 77% → 67%

## Para Formatação/Otimização (Janeiro 2025)

### 1. Backup Essencial
```bash
# Projetos
/media/juan/DATA/projetos/PROJETO-MAXIMUS-AGENTIC

# Configs importantes
~/.bashrc, ~/.zshrc, ~/.gitconfig
~/.ssh/
~/.aws/
```

### 2. Otimizações Pós-Instalação
```bash
# Swap otimizado (SSD)
sudo sysctl vm.swappiness=10
sudo sysctl vm.vfs_cache_pressure=50

# Limitar journald
sudo journalctl --vacuum-size=100M
echo "SystemMaxUse=100M" | sudo tee -a /etc/systemd/journald.conf

# Auto-limpeza de cache (cron semanal)
echo "0 3 * * 0 find ~/.cache -type f -atime +7 -delete" | crontab -
```

### 3. Navegador
- **Usar APENAS 1 navegador** (Chrome OU Chromium)
- Instalar: "The Great Suspender" ou "Auto Tab Discard"
- Limitar abas simultâneas (max 10-15)

### 4. Desenvolvimento
```bash
# Limpar caches automaticamente
npm config set cache-min 1
pip config set global.cache-dir /tmp/pip-cache
```

### 5. Monitoramento
```bash
# Instalar htop/btop para monitorar
sudo apt install btop

# Alias úteis (.bashrc)
alias cleancache='rm -rf ~/.cache/pip* ~/.cache/go-build ~/.cache/npm'
alias diskspace='df -h && du -sh ~/.cache'
```

## Scripts de Manutenção

### cleanup.sh (rodar mensalmente)
```bash
#!/bin/bash
rm -rf ~/.cache/pip-tools/*
rm -rf ~/.cache/go-build/*
rm -rf ~/.cache/chromium/*
npm cache clean --force
sudo journalctl --vacuum-time=7d
sudo apt-get clean && sudo apt-get autoclean
echo "Limpeza completa!"
```

## Hardware Desejado (upgrade)
- RAM: 32GB (dobro)
- SSD: 512GB+ NVMe
- CPU: Mínimo 6 cores/12 threads

---
**Criado**: 03/12/2024
**Para execução**: Janeiro 2025
