/*
 *
 *
 *
 */

Ext.define('RnaFolder',
    {
        extend: 'Ext.panel.Panel',
        title: 'RNA Folder',
        layout: 'fit',
        tpl: '',
        closable: true,
        autoScroll: true,
        html: '<iframe style="overflow:auto;width:100%;height:100%;" frameborder="0"  src="http://biofab.jbei.org/webtools/rnafold.html"></iframe>',

        constructor: function() {

            this.items = [];
            this.callParent();
        }
    }
);
