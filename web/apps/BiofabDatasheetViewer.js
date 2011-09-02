/*
 *
 *  Developed by:
 *   
 *      Cesar A. Rodriguez
 *
 */

Ext.define('BiofabDatasheetViewer',
    {
        extend: 'Ext.panel.Panel',
        id: 'biofabDatasheetViewer',
        title: 'BIOFAB Datasheets',
        layout: 'fit',
        closable: true,
        autoScroll: true,
        html: '<iframe style="overflow:auto;width:100%;height:100%;" frameborder="0"  src="./dac/index.html"></iframe>',

        constructor: function() {

            this.items = [];
            this.callParent();
        }
    }
);
