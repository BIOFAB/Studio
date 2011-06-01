/*
 *
 *
 *
 */

Ext.define('SequenceChecker', {
    extend: 'Ext.tab.Panel',
    title: 'Sequence Checker',
    layout: 'border',
    tpl: '',
    closable: true,
    autoScroll: true,

    constructor: function() {

        this.items = [
            {
                xtype: 'form',
                itemId:'parametersForm',
                frame: true,
                title: 'Parameters',
                bodyStyle:'padding:5px 5px 0',
                //width: 400,
                //height: 300,
                fieldDefaults: {
                    msgTarget: 'side',
                    labelWidth: 75
                },
                defaultType: 'textfield',
                defaults: {
                    anchor: '75%'
                    //width: 200
                },
                items: [
                    {
                        fieldLabel: 'Traces Folder',
                        name: 'traces',
                        allowBlank:false
                    },
                    {
                        fieldLabel: 'Start',
                        name: 'start',
                        allowBlank:false
                    },
                    {
                        fieldLabel: 'Stop',
                        name: 'company',
                        allowBlank:false
                    }
                ],
                buttons: [
                    {
                        text: 'Check'
                    },
                    {
                        text: 'Reset',
                        handler: function()
                            {
                                this.up('form').getForm().reset();
                            }
                    }
                ]
            },
            {
                xtype: 'panel',
                title: 'Result',
                layout: 'fit',
                region: 'center',
                //height: 400,
                split: true,
                ref: 'resultPanel',
                html: '<iframe style="overflow:auto;width:100%;height:100%;" frameborder="0"  src="http://biofab.jbei.org/python/checkseq_output/summary.html"></iframe>'
//              items: []
            }
        ];

        this.callParent();
    }
});
