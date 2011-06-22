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
                url: 'http://biofab.jbei.org/studio/app.py',
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
                        name: 'stop',
                        allowBlank:false
                    }
                ],
                buttons: [
                    {
                        text: 'Check',
                        handler: function() {
                            var form = this.up('form').getForm();
                            //var tabPanel = this.up('tabpanel');
                            //form.tabPanel = tabPanel;
                            
                            if (form.isValid())
                            {
                                form.submit(
                                    {
                                        success: function(form, action)
                                        {
//                                            var htmlString = '<p>The result will go here.</p>'
//                                                                + '<p>The variables you sent are:</p>'
//                                                                + '<p>Traces Folder: ' + action.result.traces + '</p>'
//                                                                + '<p>Start: ' + action.result.start + '</p>'
//                                                                + '<p>Stop: '+ action.result.stop +'</p>'
//                                                                + '<p>HTML: '+ action.result.html +'</p>';
                                            var resultPanel = Ext.create('Ext.panel.Panel',
                                                {
                                                    bodyPadding: 5,
                                                    closable: true,
                                                    title: 'Result',
                                                    //html: htmlString
                                                    html:'<iframe src="http://biofab.jbei.org/studio/checkseq_output/summary.html" width="100%" height="100%"></iframe>'
                                                }
                                            );
                                            var tabPanel = form.owner.up('tabpanel');
                                            var tab = tabPanel.add(resultPanel);
                                            tabPanel.setActiveTab(tab);

                                            //Ext.Msg.alert('Success', action.result.msg);
                                        },
                                        failure: function(form, action)
                                                    {
                                                        Ext.Msg.alert('Failed', action.result.msg);
                                                    }
                                    }
                                );
                            }
                        }
                    },
                    {
                        text: 'Reset',
                        handler: function()
                            {
                                this.up('form').getForm().reset();
                            }
                    }
                ]
            }
//            {
//                xtype: 'panel',
//                title: 'Result',
//                layout: 'fit',
//                //region: 'center',
//                //height: 400,
//                split: true,
//                ref: 'resultPanel',
//                html: '<iframe style="overflow:auto;width:100%;height:100%;" frameborder="0"  src="http://biofab.jbei.org/python/checkseq_output/summary.html"></iframe>'
////              items: []
//            }
        ];

        this.callParent();
    }

//    submitSuccessHandler: function(form, action)
//    {
//        var htmlString = '<p>The result will go here.\n'
//                            + 'The variables you sent are:'
//                            + 'Traces Folder: ' + action.result.traces
//                            + 'Start: ' + action.result.start
//                            + 'Stop: '+ action.result.stop +'</p>';
//        var resultPanel = Ext.create('Ext.panel.Panel',
//            {
//                bodyPadding: 5,
//                title: 'Result',
//                html: htmlString
//            }
//        );
//        //var tabPanel = form.up('tabpanel');
//        var tab = this.add(resultPanel);
//        this.setActiveTab(tab);
//
//        //Ext.Msg.alert('Success', action.result.msg);
//    }

//    submitSuccessHandler: function(form, action)
//    {
//        var htmlString = '<p>The result will go here.\n'
//                            + 'The variables you sent are:'
//                            + 'Traces Folder: ' + action.result.traces
//                            + 'Start: ' + action.result.start
//                            + 'Stop: '+ action.result.stop +'</p>';
//        var resultPanel = Ext.create('Ext.panel.Panel',
//            {
//                bodyPadding: 5,
//                title: 'Result',
//                html: htmlString
//            }
//        );
//        var tabPanel = this.getComponent('centerTabPanel');
//        var tab = this.add(resultPanel);
//        this.setActiveTab(tab);
//
//        //Ext.Msg.alert('Success', action.result.msg);
//    },

//    submiFailureHandler: function(form, action)
//    {
//        Ext.Msg.alert('Failed', action.result.msg);
//    }
});
