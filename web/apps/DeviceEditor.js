/*
 *
 *
 *
 */

Ext.define('DeviceEditor',
    {
        extend: 'Ext.panel.Panel',
        id: 'deviceEditor',
        title: 'Device Editor',
        layout: 'auto',
        closable: true,
        autoScroll: true,
        html: '<iframe style="overflow:auto;width:100%;height:100%;" frameborder="0"  src="http://j5.jbei.org/bin/deviceeditor.pl"></iframe>',

        constructor: function() {

            this.items = [];
            this.callParent();
        }
    }
);
