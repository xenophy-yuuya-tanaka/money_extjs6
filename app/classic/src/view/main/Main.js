/**
 * This class is the main view for the application. It is specified in app.js as the
 * "mainView" property. That setting automatically applies the "viewport"
 * plugin causing this view to become the body element (i.e., the viewport).
 *
 * TODO - Replace this content of this view to suite the needs of your application.
 */
Ext.define('Money.view.main.Main', {
    extend: 'Ext.tab.Panel',
    xtype: 'app-main',

    requires: [
        'Ext.plugin.Viewport',
        'Ext.window.MessageBox',
        'Money.view.main.MainController',
        'Money.view.main.MainModel',
        'Money.view.main.List',
        'Money.view.payment.Panel'
    ],

    controller: 'main',
    viewModel: 'main',

    ui: 'navigation',

    tabBarHeaderPosition: 1,
    titleRotation: 0,
    tabRotation: 0,

    header: {
        layout: {
            align: 'stretchmax'
        },
        title: {
            bind: {
                text: '{name}'
            },
            flex: 0
        },
        iconCls: 'fa-th-list'
    },

    tabBar: {
        flex: 1,
        layout: {
            align: 'stretch',
            overflowHandler: 'none'
        }
    },

    responsiveConfig: {
        tall: {
            headerPosition: 'top'
        },
        wide: {
            headerPosition: 'left'
        }
    },

    defaults: {
        bodyPadding: 0,
        tabConfig: {
            plugins: 'responsive',
            responsiveConfig: {
                wide: {
                    iconAlign: 'left',
                    textAlign: 'left'
                },
                tall: {
                    iconAlign: 'top',
                    textAlign: 'center',
                    width: 120
                }
            }
        }
    },

    items: [{
        title   : '支出',
        xtype   : 'payment-panel',
        iconCls : 'fa-home',
    }, {
        title   : '収入',
        iconCls : 'fa-user',
        html    : '収入パネル'
    }, {
        title   : 'クレジットカード',
        iconCls : 'fa-users',
        html    : 'クレジットカードパネル'
    }, {
        title   : 'カテゴリ',
        iconCls : 'fa-users',
        html    : 'カテゴリパネル'
    }, {
        title   : 'メンバ',
        iconCls : 'fa-users',
        html    : 'メンバパネル'
    }]

});
