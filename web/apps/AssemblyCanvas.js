/*
 *
 *  Developed by:
 *   
 *      Cesar A. Rodriguez
 *
 */

Ext.define('AssemblyCanvas', {
    extend: 'Ext.tab.Panel',
    id: 'assemblyCanvas',
    title: 'Assembly Canvas',
    layout: 'auto',
    closable: true,
    autoScroll: true,
    
    fileNameTokenStore: null,
    seqFileInfoStore: null,
    
    constructor: function() {
        
        if (window.File && window.FileReader && window.FileList && window.Blob) 
        {
            this.fileNameTokenStore = new Ext.data.Store({
                storeId: 'fileNameTokenStore',
                model: 'FileNameToken',
                autoLoad: false,
                sorters: [
                    {
                        property: 'position',
                        direction: 'ASC'
                    }
                ]
            });

            this.seqFileInfoStore = new Ext.data.Store({
                storeId: 'seqFileInfoStore',
                model: 'LocalFile',
                autoLoad: false,
                sorters: [
                    {
                        property: 'name',
                        direction: 'ASC'
                    }
                ]
            });

            this.items = [
                {
                    xtype: 'panel',
                    title: 'Sequence Check',
                    //layout: {type:'vbox', padding:'0', align:'stretch'},
                    layout: 'border',
                    itemId: 'sequenceCheckPanel',
                    items: [
                        {
                            xtype: 'panel',
                            itemId:'sequenceCheckParametersPanel',
                            //frame: true,
                            title: 'Parameters',
                            collapsible: true,
                            layout: 'border',
                            region: 'center',
                            split: false,
                            //height: 400,
                            flex: 2,
                            //maxheight: 400,
                            //minheight: 400,
                            //url: 'http://biofab.jbei.org/studio/app.py',
                            bbar: [
                                {xtype: 'tbfill'},
                                {
                                    xtype: 'button',
                                    text: 'Check Sequences',
                                    disabled: true,
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
                                {xtype: 'tbfill'}
    //                            {
    //                                xtype: 'button',
    //                                text: 'Reset',
    //                                handler: function()
    //                                    {
    //                                        this.up('form').getForm().reset();
    //                                    }
    //                            }
                            ],
                            items: [
                                {
                                    xtype: 'panel',
                                    itemId: 'fileSelectionPanel',
                                    title: '',
                                    region: 'center',
                                    split: true,
                                    layout: 'border',
                                    //layout: {type:'vbox', padding:'0', align:'stretch'},
                                    flex: 1,
                                    items: [
                                        {
                                          xtype: 'panel',
                                          title: 'File Selection',
                                          region: 'north',
                                          split: false,
                                          height: 70,
                                          items: [
                                              {
                                                // TODO Look for solution that doesn't require a static id
                                                xtype: 'field',
                                                html: '<input id="assemblyCanvasFiles" type="file" name="files[]" multiple />',
                                                padding: '15 10 10 15'
                                              }
                                          ]
                                        },
                                        {
                                            xtype: 'gridpanel',
                                            itemId: 'seqFileInfoGridPanel',
                                            title: 'Selected Files',
                                            store: this.seqFileInfoStore,
                                            region: 'center',
                                            flex: 1,
                                            split: true,
                                            columns: [
                                                {header: 'Name',  dataIndex: 'name', flex:1},
                                                {header: 'Size (bytes)', dataIndex: 'size'}
                                            ]
                                        },
                                        {
                                            xtype: 'gridpanel',
                                            itemId: 'seqFileTokenGridPanel',
                                            title: 'File Name Tokens',
                                            store: this.fileNameTokenStore,
                                            flex: 1,
                                            region: 'south',
                                            split: true,
                                            columns: [
                                                {header: 'Position',  dataIndex: 'position'},
                                                {header: 'Token', dataIndex: 'token'},
                                                {header: 'Type', dataIndex: 'type', flex:1}
                                            ]
                                        }
                                    ]
                                },
                                {
                                    xtype: 'panel',
                                    itemId: 'otherParametersPanel',
                                    title: 'Other Parameters',
                                    region: 'east',
                                    split: true,
                                    defaults: {anchor: '75%'},
                                    fieldDefaults: {
                                        msgTarget: 'side',
                                        labelWidth: 75
                                    },
                                    flex: 1,
                                    bodyStyle:'padding: 5px 5px 0',
                                    layout: {type:'vbox', padding:'0', align:'stretch'},
                                    items: [
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'Start',
                                            name: 'start',
                                            allowBlank:false
                                        },
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'Stop',
                                            name: 'stop',
                                            allowBlank:false
                                        } 
                                    ]
                                }
                            ]
                        },
    //                    {
    //                        xtype: 'panel',
    //                        //id: 'assemblyCanvas.list',
    //                        //itemId: 'sequenceCheckResultsPanel',
    //                        title: 'File Input',
    //                        height: 100,
    //                        html: '<input type="file" id="assemblyCanvas.files" name="files[]" multiple />' //'<iframe style="overflow:auto;width:100%;height:100%;" frameborder="0"  src="http://biofab.jbei.org/python/checkseq_output/summary.html"></iframe>'
    //                    },
                        {
                            xtype: 'panel',
                            //id: 'assemblyCanvasSequenceCheckResultsPanel',
                            itemId: 'sequenceCheckResultsPanel',
                            title: 'Results',
                            flex: 1,
                            region: 'south',
                            split: false,
                            //layout: 'border',
                            html: 'Results will go here.', //'<iframe style="overflow:auto;width:100%;height:100%;" frameborder="0"  src="http://biofab.jbei.org/python/checkseq_output/summary.html"></iframe>'
                            items: []
                        }
                    ]
                }
            ];

            this.callParent();
            this.on('afterrender', this.handleAfterRender, this, null);
        }
        else 
        {
            this.items = [
                {
                    xtype: 'panel',
                    title: 'Browser Requirements',
                    html: '<h1>&nbsp;</h1><h1>&nbsp;</h1><h1>&nbsp;</h1>'
                           +'<h1 align=center>Browser Requirements</h1>'
                           + '<p align=center>The Assembly Canvas requires a browser that implements the file management functions of HTML 5.0.</p>'
                           + '<p align=center>The recommended browser is <a href="http://www.google.com/chrome" target="_blank"><b>Google Chrome version 13.0 and above<b></a></p>'
                }
            ];
            
            this.callParent();
        }
    },
    
    handleAfterRender: function(component, options)
    {
        // TODO Find a solution that doesn't require direct accessing of the DOM node
        
        var domNode = Ext.getDom('assemblyCanvasFiles');
        domNode.addEventListener('change', this.handleFileSelect, false);
    },
        
    handleFileSelect: function(event)
    {
        var files; 
        var fileInfo = [];
        var firstFile;
        var tokens =[];
        var classifiedTokens = [];
        var store;
        var count;
        
        files = event.target.files;
        firstFile = files[0];
        tokens = firstFile.name.split('_');
      
        for(var i = 0, file; file = files[i]; i++) 
        {
          fileInfo.push(
            {
                name: file.name, 
                size: file.size
            });
        }
        
        for(var j = 0, token; token = tokens[j]; j++) 
        {
          classifiedTokens.push(
            {
                position: j, 
                token: token,
                type: 'IGNORE'
            });
        }
        
        store = Ext.getStore ('seqFileInfoStore');
        count = store.getCount();
        
        for(var k = 0; k < count; k++) 
        {
          store.removeAt(0);
        }
        
        store.add(fileInfo);
        
        store = Ext.getStore ('fileNameTokenStore');
        count = store.getCount();
        
        for(var l = 0; l < count; l++) 
        {
          store.removeAt(0);
        }
        
        store.add(classifiedTokens);
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
