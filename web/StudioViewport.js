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
    plasmidGridPanel: null,
    
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
                                text: 'RNA Folder',
                                id: 'rnaFolderButton'
                            },
                            {
                                xtype: 'tbseparator'
                            },
                            {
                                xtype: 'button',
                                text: 'Device Editor',
                                id: 'deviceEditorButton',
                                disabled: false
                            },
                            {
                                xtype: 'tbseparator'
                            },
                            {
                                xtype: 'button',
                                text: 'Sequence Checker',
                                id: 'checkerButton',
                                disabled: true
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
        button = Ext.ComponentManager.get('rnaFolderButton');
        button.setHandler(this.rnaFolderButtonClickHandler, this);
        button = Ext.ComponentManager.get('checkerButton');
        button.setHandler(this.checkerButtonClickHandler, this);
        button = Ext.ComponentManager.get('deviceEditorButton');
        button.setHandler(this.deviceEditorButtonClickHandler, this);
         
        this.showBiofabExchange();
    },
	
/**********************
 * 
 *  Protected Methods
 * 
 **********************/
    
    showPlasmidViewer: function(plasmidRecord)
    {
        var plasmidViewer;
        var tab;

        plasmidViewer = new PlasmidViewer();

        if(plasmidViewer !== null)
        {
            tab = this.centerTabPanel.add(plasmidViewer);
            this.centerTabPanel.setActiveTab(tab);
            plasmidViewer.displayInfo(plasmidRecord);
        }
    },
    
    showBiofabExchange: function()
    {
        var viewer = Ext.ComponentManager.get('biofabExchange');
                
        if(viewer === undefined)
        {
            viewer = new BiofabExchange();
            this.centerTabPanel.add(viewer);
            this.centerTabPanel.setActiveTab(viewer);
        }
        else
        {
            this.centerTabPanel.setActiveTab(viewer);
        }
    },
    
/**********************
 * 
 *  Event Handlers
 * 
 **********************/
    
    plasmidGridStoreLoadHandler: function(store, records, isSuccessful, operation, options)
    {
        var record = records[0];
        this.showPlasmidViewer(record);
    },
    
    plasmidGridRowSelectHandler: function(selectModel, records, options)
    {
        var record = records[0];
        this.showPlasmidViewer(record);
    },
    
    biofabExchangeButtonClickHandler:function(button, event)
    {
        this.showBiofabExchange();
    },
    
    rnaFolderButtonClickHandler:function(button, event)
    {
        var folder = new RnaFolder();
        var tab = this.centerTabPanel.add(folder);
        this.centerTabPanel.setActiveTab(tab);
    },

    deviceEditorButtonClickHandler: function(button, event)
    {
        var editor = new DeviceEditor();
        var tab = this.centerTabPanel.add(editor);
        this.centerTabPanel.setActiveTab(tab);
    },

    checkerButtonClickHandler: function(button, event)
    {
        var checker = new SequenceChecker();
        var tab = this.centerTabPanel.add(checker);
        this.centerTabPanel.setActiveTab(tab);
    }
});
