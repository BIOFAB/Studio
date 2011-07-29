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
        
        Ext.define('Plasmid', {
            extend: 'Ext.data.Model',
            fields: [
                {name: 'biofabId',  type: 'string'},
                {name: 'description', type: 'string'},
                {name: 'index', type: 'int'}
            ]
        });

       var plasmidStore = new Ext.data.Store({
           model: 'Plasmid',
           proxy: {
               type: 'ajax',
               url : './plasmids',
               reader: 'json'
           },
           autoLoad: true,
           sorters: [
                {
                    property : 'index',
                    direction: 'ASC'
                }
           ]
       });

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
                width: 400,
                style: '',
                collapsible: true,
                region: 'west',
                split: true,
                id: 'westTabPanel',
                items: [
                    {
                        xtype: 'grid',
                        id: 'plasmidGridPanel',
                        title: 'Plasmids',
                        store: plasmidStore,
                        stripeRows: true,
                        columnLines: true,
                        autoExpandColumn: 1,
                        columns: [
                            {
                                xtype: 'gridcolumn',
                                dataIndex: 'biofabId',
                                header: 'Identifier',
                                sortable: true,
                                width: 100
                                //editable: false
                            },
                            {
                                xtype: 'gridcolumn',
                                header: 'Description',
                                sortable: true,
                                width: 300,
                                //editable: false,
                                dataIndex: 'description'
                            }
                        ]
                    }
                ]
            }
        ];
        
        this.callParent();
        
        this.centerTabPanel = this.getComponent('centerTabPanel');
        this.plasmidGridPanel = Ext.ComponentManager.get('plasmidGridPanel');
        var plasmidGridSelectionModel = this.plasmidGridPanel.getSelectionModel();
	plasmidGridSelectionModel.on('selectionchange', this.plasmidGridRowSelectHandler, this);
        button = Ext.ComponentManager.get('rnaFolderButton');
        button.setHandler(this.rnaFolderButtonClickHandler, this);
        button = Ext.ComponentManager.get('checkerButton');
        button.setHandler(this.checkerButtonClickHandler, this);
        button = Ext.ComponentManager.get('deviceEditorButton');
        button.setHandler(this.deviceEditorButtonClickHandler, this);
        
        this.plasmidGridPanel.getStore().on('load', this.plasmidGridStoreLoadHandler, this, null);
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
