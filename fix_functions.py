#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 HTML 中的函数定义顺序问题
将所有配置管理相关的函数移到页面顶部
"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 在第一个 </script> 标签之前添加所有配置管理函数的声明
# 这样它们在页面加载时就立即可用

additional_functions = '''
        // ==================== 配置管理函数（提前声明）====================
        let currentConfigId = null;
        let allConfigs = [];
        let autoRefreshInterval = null;

        // 这些函数的完整实现在后面，这里先声明为全局函数
        window.createConfig = async function() {
            const data = {
                name: document.getElementById('configName').value.trim(),
                driver: document.getElementById('configDriver').value,
                host: document.getElementById('configHost').value.trim(),
                port: parseInt(document.getElementById('configPort').value),
                database: document.getElementById('configDatabase').value.trim(),
                catalog: document.getElementById('configCatalog').value.trim() || null,
                user: document.getElementById('configUser').value.trim(),
                password: document.getElementById('configPassword').value
            };

            if (!data.name || !data.host || !data.database || !data.user || !data.password) {
                alert('请填写所有必填字段');
                return;
            }

            try {
                const response = await fetch('/api/configs', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (result.success) {
                    // 激活新创建的配置
                    const activateResponse = await fetch(`/api/configs/${result.config.id}/activate`, {
                        method: 'POST'
                    });
                    if (activateResponse.ok) {
                        alert('配置创建并激活成功！');
                        if (typeof loadConfigs === 'function') {
                            await loadConfigs();
                        }
                        if (typeof checkConnectionStatus === 'function') {
                            checkConnectionStatus();
                        }
                        closeConfigModal();
                    }
                } else {
                    alert('创建失败: ' + result.error);
                }
            } catch (error) {
                alert('创建失败: ' + error.message);
            }
        };

        window.saveConfig = async function() {
            if (!currentConfigId) return;

            const data = {
                name: document.getElementById('configName').value.trim(),
                driver: document.getElementById('configDriver').value,
                host: document.getElementById('configHost').value.trim(),
                port: parseInt(document.getElementById('configPort').value),
                database: document.getElementById('configDatabase').value.trim(),
                catalog: document.getElementById('configCatalog').value.trim() || null,
                user: document.getElementById('configUser').value.trim()
            };

            const password = document.getElementById('configPassword').value;
            if (password) {
                data.password = password;
            }

            try {
                const response = await fetch(`/api/configs/${currentConfigId}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (result.success) {
                    alert('保存成功！');
                    if (typeof loadConfigs === 'function') {
                        await loadConfigs();
                    }
                } else {
                    alert('保存失败: ' + result.error);
                }
            } catch (error) {
                alert('保存失败: ' + error.message);
            }
        };

        window.deleteConfig = async function() {
            if (!currentConfigId) return;
            if (!confirm('确定要删除这个配置吗？')) return;

            try {
                const response = await fetch(`/api/configs/${currentConfigId}`, {
                    method: 'DELETE'
                });

                const result = await response.json();
                if (result.success) {
                    alert('删除成功！');
                    if (typeof loadConfigs === 'function') {
                        await loadConfigs();
                    }
                    if (typeof checkConnectionStatus === 'function') {
                        checkConnectionStatus();
                    }
                    document.getElementById('configForm').innerHTML = '<div style="text-align: center; color: #999; padding: 50px;"><p style="font-size: 16px;">请选择或创建一个配置</p></div>';
                } else {
                    alert('删除失败: ' + result.error);
                }
            } catch (error) {
                alert('删除失败: ' + error.message);
            }
        };

        window.activateConfig = async function() {
            if (!currentConfigId) return;

            try {
                const response = await fetch(`/api/configs/${currentConfigId}/activate`, {
                    method: 'POST'
                });

                const result = await response.json();
                if (result.success) {
                    alert('配置已激活！');
                    if (typeof loadConfigs === 'function') {
                        await loadConfigs();
                    }
                    if (typeof checkConnectionStatus === 'function') {
                        checkConnectionStatus();
                    }
                } else {
                    alert('激活失败: ' + result.error);
                }
            } catch (error) {
                alert('激活失败: ' + error.message);
            }
        };

        window.testConnection = async function() {
            if (!currentConfigId) return;

            try {
                const response = await fetch('/api/configs/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({config_id: currentConfigId})
                });

                const result = await response.json();
                if (result.success) {
                    alert('连接成功！\\n' + result.message);
                } else {
                    alert('连接失败！\\n' + result.message);
                }
            } catch (error) {
                alert('测试失败: ' + error.message);
            }
        };

        window.selectConfig = async function(configId) {
            currentConfigId = configId;
            const config = allConfigs.find(c => c.id === configId);
            if (!config) return;

            document.getElementById('configForm').innerHTML = `
                <h3 style="margin-bottom: 20px; color: #333;">配置详情</h3>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; color: #666; font-weight: bold;">配置名称</label>
                    <input type="text" id="configName" value="${config.name}"
                           style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; color: #666; font-weight: bold;">数据库类型</label>
                    <select id="configDriver" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px;">
                        <option value="mysql" ${config.driver === 'mysql' ? 'selected' : ''}>MySQL</option>
                        <option value="starrocks" ${config.driver === 'starrocks' ? 'selected' : ''}>StarRocks</option>
                        <option value="doris" ${config.driver === 'doris' ? 'selected' : ''}>Doris</option>
                        <option value="postgresql" ${config.driver === 'postgresql' ? 'selected' : ''}>PostgreSQL</option>
                    </select>
                </div>
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 15px; margin-bottom: 20px;">
                    <div>
                        <label style="display: block; margin-bottom: 8px; color: #666; font-weight: bold;">主机地址</label>
                        <input type="text" id="configHost" value="${config.host}" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px;">
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 8px; color: #666; font-weight: bold;">端口</label>
                        <input type="number" id="configPort" value="${config.port}" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px;">
                    </div>
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; color: #666; font-weight: bold;">数据库名</label>
                    <input type="text" id="configDatabase" value="${config.database}" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; color: #666; font-weight: bold;">Catalog (可选)</label>
                    <input type="text" id="configCatalog" value="${config.catalog || ''}" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; color: #666; font-weight: bold;">用户名</label>
                    <input type="text" id="configUser" value="${config.user}" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px;">
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; color: #666; font-weight: bold;">密码</label>
                    <div style="position: relative;">
                        <input type="password" id="configPassword" value="" placeholder="留空表示不修改" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px;">
                        <button onclick="togglePassword()" type="button" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 18px;">👁️</button>
                    </div>
                </div>
                <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                    <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                        <input type="checkbox" id="autoRefreshToggle" onchange="toggleAutoRefresh()" style="cursor: pointer; width: 18px; height: 18px;">
                        <div>
                            <div style="font-weight: bold; color: #333;">启用自动刷新</div>
                            <div style="font-size: 12px; color: #666; margin-top: 4px;">每30秒自动检测数据库表和视图的变化</div>
                        </div>
                    </label>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 30px;">
                    <button onclick="testConnection()" style="flex: 1; padding: 12px; background: #2196f3; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">测试连接</button>
                    <button onclick="saveConfig()" style="flex: 1; padding: 12px; background: #4caf50; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">保存</button>
                    <button onclick="activateConfig()" style="flex: 1; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">激活</button>
                    <button onclick="deleteConfig()" style="padding: 12px 20px; background: #f44336; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">删除</button>
                </div>
            `;
        };

        window.loadConfigs = async function() {
            try {
                const response = await fetch('/api/configs');
                const data = await response.json();
                allConfigs = data.configs;
                const activeConfigId = data.active_config_id;

                const listEl = document.getElementById('configList');
                if (!listEl) return;

                if (allConfigs.length === 0) {
                    listEl.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">暂无配置</div>';
                    return;
                }

                listEl.innerHTML = allConfigs.map(config => `
                    <div onclick="selectConfig('${config.id}')"
                         style="padding: 15px; margin-bottom: 10px; border-radius: 8px; cursor: pointer; background: ${config.id === activeConfigId ? '#e8eaf6' : '#f9f9f9'}; border: 2px solid ${config.id === activeConfigId ? '#667eea' : 'transparent'};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: bold; color: #333; margin-bottom: 5px;">
                                    ${config.id === activeConfigId ? '✓ ' : ''}${config.name}
                                </div>
                                <div style="font-size: 12px; color: #666;">
                                    ${config.driver} - ${config.host}:${config.port}
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('加载配置失败:', error);
            }
        };

        window.checkConnectionStatus = async function() {
            try {
                const response = await fetch('/api/configs/active');
                if (response.ok) {
                    const data = await response.json();
                    updateConnectionStatus(true, data.config.name);
                } else {
                    updateConnectionStatus(false, '未配置');
                }
            } catch (error) {
                updateConnectionStatus(false, '未配置');
            }
        };

        function updateConnectionStatus(connected, text) {
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');

            if (statusDot && statusText) {
                if (connected) {
                    statusDot.style.background = '#4caf50';
                    statusText.textContent = text;
                } else {
                    statusDot.style.background = '#ffc107';
                    statusText.textContent = text;
                }
            }
        }

        // 页面加载时检查连接状态
        window.addEventListener('load', function() {
            checkConnectionStatus();
            if (typeof loadConfigs === 'function') {
                loadConfigs();
            }
        });
'''

# 找到第一个 </script> 标签的位置
first_script_end = content.find('</script>')
if first_script_end != -1:
    # 在第一个 </script> 之前插入额外的函数
    content = content[:first_script_end] + additional_functions + '\n    ' + content[first_script_end:]

# 保存修改后的文件
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Function definitions moved to page top')
print('All configuration management functions are now available on page load')
