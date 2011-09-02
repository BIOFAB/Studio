/*
 * 
 * File: StudioViewport.js
 *
 */

 Ext.define('StudioViewport', {
    extend: 'Ext.container.Viewport',
    layout: 'border',
    id: 'studioViewport',
    centerTabPanel: null,
    westTabPanel: null,
    
    constructor: function() {
        var button;
        
        this.items = [
            {
                xtype: 'tabpanel',
                activeTab: 0,
                region: 'center',
                split: true,
                id: 'centerTabPanel',
                items:[]
            },
            {
                xtype: 'panel',
                region: 'north',
                layout: 'fit',
                height: 30,
                id: 'northPanel',
                items: [
                    {
                        xtype: 'toolbar',
                        id: 'mainToolbar',
                        items: [
                            {
                                xtype: 'button',
                                text: 'BIOFAB Exchange',
                                id: 'biofabExchangeButton'
                            },
                            {
                                xtype: 'tbseparator'
                            },
                            {
                                xtype: 'button',
                                text: 'BIOFAB Datasheets',
                                id: 'biofabDatasheetsButton'
                            },
                            {
                                xtype: 'tbseparator'
                            },
                            {
                                xtype: 'button',
                                text: 'RNA Folder',
                                id: 'rnaFolderButton'
                            },
                            {
                                xtype: 'tbseparator'
                            },
                            {
                                xtype: 'button',
                                text: 'Assembly Canvas',
                                id: 'assemblyCanvasButton',
                                disabled: false
                            },
                            {
                                xtype: 'tbseparator'
                            },
                            {
                                xtype: 'button',
                                text: 'Device Editor',
                                id: 'deviceEditorButton',
                                disabled: false
                            }
                        ]
                    }
                ]
            },
            {
                xtype: 'tabpanel',
                activeTab: 0,
                width: 250,
                style: '',
                collapsible: true,
                region: 'west',
                split: true,
                id: 'westTabPanel',
                items: [
                    {
                        xtype: 'panel',
                        title: 'Projects',
                        html: '<b>A tree view with your personal collection of components will be added in an upcoming release of the BIOFAB Studio</b>'
                    },
                ]
            }
        ];
        
        this.callParent();
        
        this.centerTabPanel = this.getComponent('centerTabPanel');
        button = Ext.ComponentManager.get('biofabExchangeButton');
        button.setHandler(this.biofabExchangeButtonClickHandler, this);
        button = Ext.ComponentManager.get('biofabDatasheetsButton');
        button.setHandler(this.handleBiofabDatasheetsButtonClick, this);
        button = Ext.ComponentManager.get('rnaFolderButton');
        button.setHandler(this.rnaFolderButtonClickHandler, this);
        button = Ext.ComponentManager.get('assemblyCanvasButton');
        button.setHandler(this.assemblyCanvasButtonClickHandler, this);
        button = Ext.ComponentManager.get('deviceEditorButton');
        button.setHandler(this.deviceEditorButtonClickHandler, this);
        
        this.westTabPanel = Ext.ComponentManager.get('westTabPanel');
         
        this.showBiofabExchange();
    },
	
/**********************
 * 
 *  Protected Methods
 * 
 **********************/
    
//    showPlasmidViewer: function(plasmidRecord)
//    {
//        var plasmidViewer;
//        var tab;
//
//        plasmidViewer = new PlasmidViewer();
//
//        if(plasmidViewer !== null)
//        {
//            tab = this.centerTabPanel.add(plasmidViewer);
//            this.centerTabPanel.setActiveTab(tab);
//            plasmidViewer.displayInfo(plasmidRecord);
//        }
//    },
    
    showBiofabExchange: function()
    {
        var app = Ext.ComponentManager.get('biofabExchange');
                
        if(app === undefined)
        {
            app = new BiofabExchange();
            this.centerTabPanel.add(app);
            this.centerTabPanel.setActiveTab(app);
        }
        else
        {
            this.centerTabPanel.setActiveTab(app);
        }
    },
    
    showBiofabDatasheetViewer: function()
    {
        var app = Ext.ComponentManager.get('biofabDatasheetViewer');
        this.westTabPanel.collapse(Ext.Component.DIRECTION_LEFT, false, null);
        
        if(app === undefined)
        {
            app = new BiofabDatasheetViewer();
            this.centerTabPanel.add(app);
            this.centerTabPanel.setActiveTab(app);
        }
        else
        {
            this.centerTabPanel.setActiveTab(app);
        }
    },
    
    showAssemblyCanvas: function()
    {
        
        var app = Ext.ComponentManager.get('assemblyCanvas');
                
        if(app === undefined)
        {
            app = new AssemblyCanvas();
            this.centerTabPanel.add(app);
            this.centerTabPanel.setActiveTab(app);
        }
        else
        {
            this.centerTabPanel.setActiveTab(app);
        }
    },
    
/**********************
 * 
 *  Event Handlers
 * 
 **********************/
    
//    plasmidGridStoreLoadHandler: function(store, records, isSuccessful, operation, options)
//    {
//        var record = records[0];
//        this.showPlasmidViewer(record);
//    },
//    
//    plasmidGridRowSelectHandler: function(selectModel, records, options)
//    {
//        var record = records[0];
//        this.showPlasmidViewer(record);
//    },
    
    biofabExchangeButtonClickHandler:function(button, event)
    {
        this.showBiofabExchange();
    },
    
    handleBiofabDatasheetsButtonClick:function(button, event)
    {
        this.showBiofabDatasheetViewer();
    },
    
    rnaFolderButtonClickHandler:function(button, event)
    {
        var app = Ext.ComponentManager.get('rnaFolder');
                
        if(app === undefined)
        {
            app = new RnaFolder();
            this.centerTabPanel.add(app);
            this.centerTabPanel.setActiveTab(app);
        }
        else
        {
            this.centerTabPanel.setActiveTab(app);
        }
    },

    deviceEditorButtonClickHandler: function(button, event)
    {
        var app = Ext.ComponentManager.get('deviceEditor');
                
        if(app === undefined)
        {
            app = new DeviceEditor();
            this.centerTabPanel.add(app);
            this.centerTabPanel.setActiveTab(app);
        }
        else
        {
            this.centerTabPanel.setActiveTab(app);
        }
    },

    assemblyCanvasButtonClickHandler: function(button, event)
    {
        this.showAssemblyCanvas();
    }
});
