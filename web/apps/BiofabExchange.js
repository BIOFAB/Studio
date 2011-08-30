/*
 * 
 * 
 *
 */

 Ext.define('BiofabExchange', {
    extend: 'Ext.tab.Panel',
    id: 'biofabExchange',
    title: "BIOFAB Exchange",
    closable: true,
    //collapsible: true,
    
    //Subcomponents
    
    plasmidsPanel: null,
    plasmidGridPanel: null,
    plasmidDesignPanel: null,
    plasmidDesignExportButton: null,
    plasmidDesignPanelText: null,
    selectedPlasmidBiofabId: null,
    oligosPanel: null,
    oligoGridPanel: null,
    oligoDesignPanel: null,
    featuresPanel: null,
    featureGridPanel: null,
    featureSequencePanel: null,
    
    constructor: function() {
       var button;
        
       var plasmidStore = new Ext.data.Store({
           model: 'Plasmid',
           proxy: {
               type: 'ajax',
               url : DAWS_BASE_URL + 'plasmids',
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
       
       var oligoStore = new Ext.data.Store({
           model: 'Oligo',
           proxy: {
               type: 'ajax',
               url : DAWS_BASE_URL + 'oligos',
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
       
       var featureStore = new Ext.data.Store({
           model: 'Feature',
           proxy: {
               type: 'ajax',
               url : DAWS_BASE_URL + 'features',
               reader: 'json'
           },
           autoLoad: true,
           sorters: [
                {
                    property : 'genbankType',
                    direction: 'ASC'
                },
                {
                    property : 'index',
                    direction: 'ASC'
                }
           ]
       });

        this.items = [
            {
                xtype: 'panel',
                itemId: 'featuresPanel',
                title: 'Features',
                layout: 'border',
                items: [
                    {
                        xtype: 'grid',
                        itemId: 'featureGridPanel',
                        region: 'center',
                        store: featureStore,
                        stripeRows: true,
                        columnLines: true,
                        //height: 300,
                        split: true,
                        columns: [
                            {
                                xtype: 'gridcolumn',
                                dataIndex: 'biofabId',
                                header: 'Identifier',
                                sortable: true,
                                width: 100
                            },
                            {
                                xtype: 'gridcolumn',
                                dataIndex: 'genbankType',
                                header: 'Genbank Type',
                                sortable: true,
                                width: 125
                            },
                            {
                                xtype: 'gridcolumn',
                                dataIndex: 'biofabType',
                                header: 'BIOFAB Type',
                                sortable: true,
                                width: 125
                            },
                            {
                                xtype: 'gridcolumn',
                                header: 'Description',
                                sortable: true,
                                width: 400,
                                flex: 1,
                                dataIndex: 'description'
                            }
                        ]
                    },
                    {
                        xtype: 'panel',
                        itemId: 'featureSequencePanel',
                        title: 'DNA Sequence',
                        region: 'south',
                        height: 250,
                        layout: 'fit',
                        split: true,
                        items:[
                            {
                                xtype: 'textarea',
                                itemId: 'featureSequenceTextArea',
                                readOnly: true
                            }
                        ]
                    }
                ]
            },
            {
                xtype: 'panel',
                itemId: 'oligosPanel',
                title: 'Oligos',
                layout: 'border',
                items: [
                    {
                        xtype: 'grid',
                        itemId: 'oligoGridPanel',
                        region: 'center',
                        store: oligoStore,
                        stripeRows: true,
                        columnLines: true,
                        //height: 300,
                        split: true,
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
                                width: 400,
                                flex: 1,
                                //editable: false,
                                dataIndex: 'description'
                            }
                        ]
                    },
                    {
                        xtype: 'panel',
                        itemId: 'oligoDesignPanel',
                        title: 'DNA Sequence',
                        region: 'south',
                        height: 250,
                        layout: 'fit',
                        split: true,
                        items:[
                            {
                                xtype: 'textarea',
                                itemId: 'oligoDesignTextArea',
                                readOnly: true
                            }
                        ]
                    }
                ]
            },
            {
                xtype: 'panel',
                itemId: 'plasmidsPanel',
                title: 'Plasmids',
                layout: 'border',
                items: [
                    {
                        xtype: 'grid',
                        itemId: 'plasmidGridPanel',
                        region: 'center',
                        store: plasmidStore,
                        stripeRows: true,
                        columnLines: true,
                        //height: 300,
                        split: true,
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
                                width: 400,
                                //editable: false,
                                dataIndex: 'description',
                                flex: 1
                            }
                        ]
                    },
                    {
                        xtype: 'panel',
                        itemId: 'plasmidDesignPanel',
                        region: 'south',
                        layout: 'fit',
                        height:500,
                        split: true,
                        tbar: {
                            xtype: 'toolbar',
                            itemId: 'plasmidDesignPanelToolbar',
                            items: [
                                {
                                    xtype: 'tbtext',
                                    itemId: 'plasmidDesignPanelText',
                                    text: 'Fetching Design...',
                                    hidden: true
                                },
                                {
                                    xtype: 'tbfill'
                                },
                                {
                                    xtype: 'button',
                                    itemId: 'plasmidDesignExportButton',
                                    text: 'Export',
                                    tooltip: 'Export the plasmid design in Genbank format.'
                                }
                            ]
                        },
                        items:[]
                    }
                ]
            }
        ];
        
        this.callParent();
        
        this.plasmidsPanel = this.getComponent('plasmidsPanel');
        this.plasmidGridPanel = this.plasmidsPanel.getComponent('plasmidGridPanel');
        this.plasmidDesignPanel = this.plasmidsPanel.getComponent('plasmidDesignPanel');
        this.plasmidDesignExportButton = this.plasmidDesignPanel.getComponent('plasmidDesignPanelToolbar').getComponent('plasmidDesignExportButton');
        this.plasmidDesignPanelText = this.plasmidDesignPanel.getComponent('plasmidDesignPanelToolbar').getComponent('plasmidDesignPanelText');
        this.plasmidDesignExportButton.setHandler(this.plasmidDesignExportButtonHandler, this);
        var plasmidGridSelectionModel = this.plasmidGridPanel.getSelectionModel();
	plasmidGridSelectionModel.on('selectionchange', this.plasmidGridRowSelectHandler, this);
        this.plasmidGridPanel.getStore().on('load', this.plasmidGridStoreLoadHandler, this, null);
        
        this.oligosPanel = this.getComponent('oligosPanel');
        this.oligoGridPanel = this.oligosPanel.getComponent('oligoGridPanel');
        this.oligoDesignPanel = this.oligosPanel.getComponent('oligoDesignPanel');
        var oligoGridSelectionModel = this.oligoGridPanel.getSelectionModel();
	oligoGridSelectionModel.on('selectionchange', this.oligoGridRowSelectHandler, this);
        this.oligoGridPanel.getStore().on('load', this.oligoGridStoreLoadHandler, this, null);
        
        this.featuresPanel = this.getComponent('featuresPanel');
        this.featureGridPanel = this.featuresPanel.getComponent('featureGridPanel');
        this.featureSequencePanel = this.featuresPanel.getComponent('featureSequencePanel');
        var featureGridSelectionModel = this.featureGridPanel.getSelectionModel();
	featureGridSelectionModel.on('selectionchange', this.featureGridRowSelectHandler, this);
        this.featureGridPanel.getStore().on('load', this.featureGridStoreLoadHandler, this, null);
    },
	
/**********************
 * 
 *  Protected Methods
 * 
 **********************/
    
    fetchPlasmidDesign:function(biofabId)
    {
        this.plasmidDesignPanelText.setVisible(true);
        Ext.Ajax.request({
                   url: DAWS_BASE_URL + 'plasmids',
                   method: "GET",
                   success: this.fetchPlasmidDesignResultHandler,
                   failure: this.fetchPlasmidDesignErrorHandler,
                   params: {
                                id: biofabId,
                                format: 'insd'
                            },
                   scope: this
        });
    },

/**********************
 * 
 *  Event Handlers
 * 
 **********************/
    
    plasmidGridStoreLoadHandler: function(store, records, isSuccessful, operation, options)
    {
        var record = records[0];
        this.selectedPlasmidBiofabId = record.get('biofabId');
        this.fetchPlasmidDesign(this.selectedPlasmidBiofabId);
    },
    
    plasmidGridRowSelectHandler: function(selectModel, records, options)
    {
        var record = records[0];
        this.selectedPlasmidBiofabId = record.get('biofabId');
        this.fetchPlasmidDesign(this.selectedPlasmidBiofabId);
    },
    
    fetchPlasmidDesignResultHandler: function(response, opts)
    {
        this.plasmidDesignPanel.removeAll(true);
        this.plasmidDesignPanelText.setVisible(false);
        var flash = {
                xtype: 'flash',
                url:'designviewer/DesignViewer.swf',
                flashVars:{design:response.responseText}
            };
        this.plasmidDesignPanel.add(flash);
    },

    fetchPlasmidDesignErrorHandler: function(response, opts)
    {
       this.plasmidDesignPanelText.setVisible(false);
       Ext.Msg.alert('Fetch Design', 'There was an error while attempting to fetch the design.\n' + 'Error: ' + response.responseText);
    },
    
    plasmidDesignExportButtonHandler: function()
    {
        var genbankWindow = window.open('./plasmids?id=' + this.selectedPlasmidBiofabId + '&format=genbank','Genbank File for ' + this.selectedPlasmidBiofabId,'width=640,height=480');
        genbankWindow.scrollbars.visible = true;
        genbankWindow.alert("Use File/Save As in the menu bar to save this document.");
        
    },
    
    oligoGridStoreLoadHandler: function(store, records, isSuccessful, operation, options)
    {
        var record = records[0];
        var biofabId = record.get('biofabId');
        var dnaSequence = record.get('dnaSequence');
        this.oligoDesignPanel.setTitle('DNA Sequence for ' + biofabId);
        this.oligoDesignPanel.getComponent('oligoDesignTextArea').setValue(dnaSequence);
    },
    
    oligoGridRowSelectHandler: function(selectModel, records, options)
    {
        var record = records[0];
        var biofabId = record.get('biofabId');
        var dnaSequence = record.get('dnaSequence');
        this.oligoDesignPanel.setTitle('DNA Sequence for ' + biofabId);
        this.oligoDesignPanel.getComponent('oligoDesignTextArea').setValue(dnaSequence);
    },
    
    featureGridStoreLoadHandler: function(store, records, isSuccessful, operation, options)
    {
        var record = records[0];
        var biofabId = record.get('biofabId');
        var dnaSequence = record.get('dnaSequence');
        this.featureSequencePanel.setTitle('DNA Sequence for ' + biofabId);
        this.featureSequencePanel.getComponent('featureSequenceTextArea').setValue(dnaSequence);
    },
    
    featureGridRowSelectHandler: function(selectModel, records, options)
    {
        var record = records[0];
        var biofabId = record.get('biofabId');
        var dnaSequence = record.get('dnaSequence');
        this.featureSequencePanel.setTitle('DNA Sequence for ' + biofabId);
        this.featureSequencePanel.getComponent('featureSequenceTextArea').setValue(dnaSequence);
    }
});
