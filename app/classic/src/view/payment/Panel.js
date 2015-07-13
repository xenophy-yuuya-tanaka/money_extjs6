/**
 *
 */
Ext.define('Money.view.payment.Panel', {

    extend: 'Ext.panel.Panel',

    requires: [
        'Money.view.payment.List',
        'Money.view.payment.Info',
        'Money.view.payment.Form'
    ],

    xtype: 'payment-panel',

    layout: 'border',

    items: [{
        region      : 'north',
        xtype       : 'payment-info',
        split       : true,
        minHeight   : 96
    }, {
        region      : 'west',
        xtype       : 'payment-form',
        split       : true,
        flex        : 1
    }, {
        region      : 'center',
        xtype       : 'payment-list',
        flex        : 2
    }]

});
