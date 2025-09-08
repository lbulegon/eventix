// desktop/electron-config.js
const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const axios = require('axios');

// Configuração da API
const API_CONFIG = {
    baseURL: 'https://eventix-development.up.railway.app/api/desktop',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    }
};

// Cliente HTTP para comunicação com a API
class ApiClient {
    constructor() {
        this.client = axios.create(API_CONFIG);
        this.token = null;
        
        // Interceptor para adicionar token automaticamente
        this.client.interceptors.request.use((config) => {
            if (this.token) {
                config.headers.Authorization = `Bearer ${this.token}`;
            }
            return config;
        });
        
        // Interceptor para lidar com respostas
        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response?.status === 401) {
                    // Token expirado, redirecionar para login
                    this.token = null;
                    this.showLoginWindow();
                }
                return Promise.reject(error);
            }
        );
    }
    
    setToken(token) {
        this.token = token;
    }
    
    async login(username, password) {
        try {
            const response = await this.client.post('/auth/login/', {
                username,
                password
            });
            
            this.setToken(response.data.access_token);
            return response.data;
        } catch (error) {
            throw new Error('Credenciais inválidas');
        }
    }
    
    async getDashboard() {
        const response = await this.client.get('/dashboard/');
        return response.data;
    }
    
    async getUsuarios() {
        const response = await this.client.get('/usuarios/');
        return response.data;
    }
    
    async getEmpresas() {
        const response = await this.client.get('/empresas/');
        return response.data;
    }
    
    async getEventos() {
        const response = await this.client.get('/eventos/');
        return response.data;
    }
    
    async getFreelancers() {
        const response = await this.client.get('/freelancers/');
        return response.data;
    }
    
    async getEstatisticas(tipo) {
        const response = await this.client.get(`/${tipo}/estatisticas/`);
        return response.data;
    }
    
    async exportarDados(tipo, formato = 'json') {
        const response = await this.client.post('/exportar-dados/', {
            tipo,
            formato
        });
        return response.data;
    }
    
    showLoginWindow() {
        // Implementar lógica para mostrar janela de login
        console.log('Redirecionando para login...');
    }
}

// Instância global do cliente API
const apiClient = new ApiClient();

// Janela principal
let mainWindow;
let loginWindow;

function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        },
        icon: path.join(__dirname, 'assets/icon.png'),
        titleBarStyle: 'default',
        show: false
    });

    // Carregar a interface principal
    mainWindow.loadFile('index.html');

    // Mostrar janela quando estiver pronta
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Menu da aplicação
    createMenu();

    // Eventos IPC para comunicação com o frontend
    setupIpcHandlers();
}

function createLoginWindow() {
    loginWindow = new BrowserWindow({
        width: 400,
        height: 500,
        resizable: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        modal: true,
        parent: mainWindow,
        show: false
    });

    loginWindow.loadFile('login.html');

    loginWindow.once('ready-to-show', () => {
        loginWindow.show();
    });

    loginWindow.on('closed', () => {
        loginWindow = null;
    });
}

function createMenu() {
    const template = [
        {
            label: 'Eventix Desktop',
            submenu: [
                {
                    label: 'Sobre',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'Sobre o Eventix Desktop',
                            message: 'Eventix Desktop v1.0.0',
                            detail: 'Aplicativo desktop para gerenciamento de eventos'
                        });
                    }
                },
                { type: 'separator' },
                {
                    label: 'Sair',
                    accelerator: 'CmdOrCtrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'Gerenciamento',
            submenu: [
                {
                    label: 'Usuários',
                    accelerator: 'CmdOrCtrl+U',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'usuarios');
                    }
                },
                {
                    label: 'Empresas',
                    accelerator: 'CmdOrCtrl+E',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'empresas');
                    }
                },
                {
                    label: 'Eventos',
                    accelerator: 'CmdOrCtrl+Shift+E',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'eventos');
                    }
                },
                {
                    label: 'Freelancers',
                    accelerator: 'CmdOrCtrl+F',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'freelancers');
                    }
                }
            ]
        },
        {
            label: 'Relatórios',
            submenu: [
                {
                    label: 'Dashboard',
                    accelerator: 'CmdOrCtrl+D',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'dashboard');
                    }
                },
                {
                    label: 'Estatísticas',
                    accelerator: 'CmdOrCtrl+S',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'estatisticas');
                    }
                },
                {
                    label: 'Exportar Dados',
                    accelerator: 'CmdOrCtrl+Shift+E',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'exportar');
                    }
                }
            ]
        },
        {
            label: 'Sistema',
            submenu: [
                {
                    label: 'Configurações',
                    accelerator: 'CmdOrCtrl+,',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'configuracoes');
                    }
                },
                {
                    label: 'Logs',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'logs');
                    }
                },
                {
                    label: 'Backup',
                    click: () => {
                        mainWindow.webContents.send('navigate', 'backup');
                    }
                }
            ]
        },
        {
            label: 'Ajuda',
            submenu: [
                {
                    label: 'Documentação',
                    click: () => {
                        require('electron').shell.openExternal('https://eventix-development.up.railway.app/api/desktop/docs/');
                    }
                },
                {
                    label: 'Suporte',
                    click: () => {
                        require('electron').shell.openExternal('mailto:suporte@eventix.com');
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

function setupIpcHandlers() {
    // Login
    ipcMain.handle('login', async (event, { username, password }) => {
        try {
            const result = await apiClient.login(username, password);
            return { success: true, data: result };
        } catch (error) {
            return { success: false, error: error.message };
        }
    });

    // Dashboard
    ipcMain.handle('get-dashboard', async () => {
        try {
            const data = await apiClient.getDashboard();
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    });

    // Usuários
    ipcMain.handle('get-usuarios', async () => {
        try {
            const data = await apiClient.getUsuarios();
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    });

    // Empresas
    ipcMain.handle('get-empresas', async () => {
        try {
            const data = await apiClient.getEmpresas();
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    });

    // Eventos
    ipcMain.handle('get-eventos', async () => {
        try {
            const data = await apiClient.getEventos();
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    });

    // Freelancers
    ipcMain.handle('get-freelancers', async () => {
        try {
            const data = await apiClient.getFreelancers();
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    });

    // Estatísticas
    ipcMain.handle('get-estatisticas', async (event, tipo) => {
        try {
            const data = await apiClient.getEstatisticas(tipo);
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    });

    // Exportar dados
    ipcMain.handle('exportar-dados', async (event, { tipo, formato }) => {
        try {
            const data = await apiClient.exportarDados(tipo, formato);
            return { success: true, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    });

    // Salvar arquivo
    ipcMain.handle('save-file', async (event, { data, filename }) => {
        try {
            const result = await dialog.showSaveDialog(mainWindow, {
                defaultPath: filename,
                filters: [
                    { name: 'JSON Files', extensions: ['json'] },
                    { name: 'CSV Files', extensions: ['csv'] },
                    { name: 'All Files', extensions: ['*'] }
                ]
            });

            if (!result.canceled) {
                const fs = require('fs');
                fs.writeFileSync(result.filePath, JSON.stringify(data, null, 2));
                return { success: true, path: result.filePath };
            }
            
            return { success: false, error: 'Operação cancelada' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    });
}

// Eventos da aplicação
app.whenReady().then(() => {
    createMainWindow();
    
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createMainWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Exportar para uso em outros arquivos
module.exports = { apiClient };
