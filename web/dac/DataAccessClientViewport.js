    /*
 * 
 * File: DataAccessClientViewport.js
 * 
 * 
 */

Ext.define('DataAccessClientViewport', { 
    extend: 'Ext.container.Viewport',
    layout: 'border',
    performanceStore: null,
    parts: null,
    collectionsGridPanel: null,
    promoterGridPanel: null,
    terminatorGridPanel: null,
    infoTabPanel: null,
    partsToolbarText: null,
	
    constructor: function()
    {
        //  Stores
        
        var promoterStore = new Ext.data.Store({
            model: 'Promoter',
            proxy: {
                type: 'ajax',
                url : '',
                reader: {type: 'json'}
            },
            sorters: [
                {
                    property : 'geneExpressionPerCell',
                    direction: 'DESC'
                }
            ],
            autoLoad: false
        });
        
        var terminatorStore = new Ext.data.Store({
            model: 'Terminator',
            proxy: {
                type: 'ajax',
                url : '',
                reader: {type: 'json'}
            },
            sorters:[
                {
                    property : 'terminationEfficiency',
                    direction: 'DESC'
                }
            ],
            autoLoad: false
        });
        
        this.items = [
            {
                xtype: 'panel',
                region: 'west',
                width: 500,
                layout: 'border',
                split: true,
                collapsible: true,
                id: 'inventoryContainer',
                items: [
                    {
                        xtype: 'grid',
                        store: 'collectionStore',
                        region: 'north',
                        split: true,
                        height: 175,
                        //autoExpandColumn: 5,
                        minColumnWidth: 60,
                        id: 'collectionsGridPanel',
                        columns: [
                            {
                                xtype: 'gridcolumn',
                                dataIndex: 'biofabID',
                                header: 'Identifier',
                                sortable: true,
                                width: 60,
                                editable: false
                            },
                            {
                                xtype: 'gridcolumn',
                                dataIndex: 'chassis',
                                header: 'Chassis',
                                sortable: true,
                                width: 60,
                                editable: false
                            },
                            {
                                xtype: 'gridcolumn',
                                dataIndex: 'name',
                                header: 'Name',
                                sortable: true,
                                width: 150,
                                editable: false
                            },
                            {
                                xtype: 'gridcolumn',
                                header: 'Version',
                                sortable: true,
                                editable: false,
                                width: 60,
                                dataIndex: 'version'
                            },
                            {
                                xtype: 'gridcolumn',
                                header: 'Release Status',
                                sortable: true,
                                editable: false,
                                width: 100,
                                dataIndex: 'releaseStatus'
                            },
                            {
                                xtype: 'gridcolumn',
                                header: 'Release Date',
                                sortable: true,
                                editable: false,
                                width: 100,
                                dataIndex: 'releaseDate'
                            }

                        ],
                        tbar: {
                            xtype: 'toolbar',
                            id: 'collectionsToolbar',
                            items: [
                                {
                                    xtype: 'tbtext',
                                    html: '<b>Collections</b>'
                                },
                                {
                                    xtype: 'tbfill'
                                },
                                {
                                    xtype: 'button',
                                    text: 'Export',
                                    tooltip: 'Export collection information in JSON format.',
                                    id: 'collectionsGridExportButton'
                                }
                            ]
                        }
                    },
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        region: 'center',
                        split: true,
                        height: 400,
                        id: 'partsTabPanel',
                        tbar:{
                            xtype: 'toolbar',
                            id: 'partsToolbar',
                            items: [
                                {
                                    xtype: 'tbtext',
                                    id: "partsToolbarText",
                                    style: {fontWeight:'bold'},
                                    text: 'Parts'
                                },
                                {
                                    xtype: 'tbfill'
                                },
                                {
                                    xtype: 'button',
                                    text: 'Show All',
                                    tooltip: 'Show all the parts',
                                    id: 'showAllPartsButton',
                                    handler: this.showAllPartsButtonHandler
                                },
                                {
                                    xtype: 'tbseparator'
                                },
                                {
                                    xtype: 'button',
                                    text: 'Export',
                                    tooltip: 'Export all the parts in CSV format',
                                    id: 'partsExportButton',
                                    handler: this.partsExportButtonHandler
                                }
                            ]
                        },
                        items:[
                            {
                                xtype: 'gridpanel',
                                id: 'promoterGridPanel',
                                title: 'Promoters',
                                store: promoterStore, 
                                columnLines: true,
                                columns: [
                                    {
                                        xtype: 'gridcolumn',
                                        dataIndex: 'displayId',
                                        header: 'Part',
                                        sortable: true,
                                        width: 80,
                                        editable: false
                                    },
                                    {
                                        xtype: 'gridcolumn',
                                        dataIndex: 'constructId',
                                        header: 'Construct',
                                        sortable: true,
                                        width: 100,
                                        editable: false
                                    },
//                                    {
//                                        xtype: 'gridcolumn',
//                                        dataIndex: 'type',
//                                        header: 'Part Type',
//                                        sortable: true,
//                                        width: 100,
//                                        editable: false
//
//                                    },
                                    {
                                        xtype: 'gridcolumn',
                                        dataIndex: 'description',
                                        header: 'Description',
                                        sortable: true,
                                        width: 175,
                                        editable: false
                                    },
                                    {
                                        xtype: 'numbercolumn',
                                        dataIndex: 'geneExpressionPerCell',
                                        header: 'Gene Expression per Cell',
                                        sortable: true,
                                        width: 150,
                                        align: 'left',
                                        editable: false,
                                        format: '0,000'
                                    },
                                    {
                                        xtype: 'numbercolumn',
                                        dataIndex: 'geneExpressionPerCellSD',
                                        header: 'Standard Deviation',
                                        sortable: true,
                                        width: 125,
                                        align: 'left',
                                        editable: false,
                                        format: '0,000.00'
                                    }
                                ]
                            },
                            {
                                xtype: 'panel',
                                title: '5\' UTRs',
                                html: '<b>5\' UTRs will be available in an upcoming release of the Data Access Client</b>'
                            },
                            {
                                xtype: 'gridpanel',
                                id: 'terminatorGridPanel',
                                title: 'Terminators',
                                store: terminatorStore, 
                                columnLines: true,
                                //stripeRows: true,
                                //features: [{ftype:'grouping'}],
                                columns: [
                                    {
                                        xtype: 'gridcolumn',
                                        dataIndex: 'displayId',
                                        header: 'Part',
                                        sortable: true,
                                        width: 80,
                                        editable: false
                                    },
                                    {
                                        xtype: 'gridcolumn',
                                        dataIndex: 'constructId',
                                        header: 'Construct',
                                        sortable: true,
                                        width: 100,
                                        editable: false
                                    },
//                                    {
//                                        xtype: 'gridcolumn',
//                                        dataIndex: 'type',
//                                        header: 'Part Type',
//                                        sortable: true,
//                                        width: 100,
//                                        editable: false
//
//                                    },
                                    {
                                        xtype: 'gridcolumn',
                                        dataIndex: 'description',
                                        header: 'Description',
                                        sortable: true,
                                        width: 175,
                                        editable: false
                                    },
                                    {
                                        xtype: 'numbercolumn',
                                        dataIndex: 'terminationEfficiency',
                                        header: 'Termination Efficiency',
                                        sortable: true,
                                        width: 150,
                                        align: 'left',
                                        editable: false,
                                        format: '0,000'
                                    },
                                    {
                                        xtype: 'numbercolumn',
                                        dataIndex: 'standardDeviation',
                                        header: 'Standard Deviation',
                                        sortable: true,
                                        width: 125,
                                        align: 'left',
                                        editable: false,
                                        format: '0,000.00'
                                    }
                                ]
                            }
                        ]
                    },
                ]
            },
            {
                xtype: 'tabpanel',
                activeTab: 0,
                region: 'center',
                split: true,
                id: 'infoTabPanel'
            }
        ];
        
        this.callParent();

        this.collectionsGridPanel = Ext.ComponentManager.get('collectionsGridPanel');
        var collectionsGridSelectionModel = this.collectionsGridPanel.getSelectionModel();
	collectionsGridSelectionModel.on('rowselect', this.collectionsGridRowSelectHandler, this);
       
	this.promoterGridPanel = Ext.ComponentManager.get('promoterGridPanel');
        var promoterGridSelectionModel = this.promoterGridPanel.getSelectionModel();
	promoterGridSelectionModel.on('rowselect', this.promoterGridRowSelectHandler, this);
        
        this.terminatorGridPanel = Ext.ComponentManager.get('terminatorGridPanel');
        var terminatorGridSelectionModel = this.terminatorGridPanel.getSelectionModel();
	terminatorGridSelectionModel.on('rowselect', this.terminatorGridRowSelectHandler, this);
        
        this.partsToolbarText = Ext.ComponentManager.get('partsToolbarText');

        var collectionsGridExportButton = Ext.ComponentManager.get('collectionsGridExportButton'); 
        collectionsGridExportButton.setHandler(this.collectionsGridExportButtonClickHandler, this);
        
        this.infoTabPanel = Ext.ComponentManager.get('infoTabPanel');
        
        this.fetchParts();
    },
    
 /**********************
 * 
 *  Protected Methods
 * 
 **********************/
        fetchParts:function()
        {
            Ext.Ajax.request({
                       url: WEB_SERVICE_BASE_URL + 'parts?format=json',
                       method: "GET",
                       success: this.fetchPartsResultHandler,
                       failure: this.fetchPartsErrorHandler,
//                       params: {
//                                    id: constructID,
//                                    format: 'json'
//                                },
                       scope: this
            });
        },
        
        fetchCollections:function()
        {
            Ext.Ajax.request({
                       url: WEB_SERVICE_BASE_URL + 'collections?format=json',
                       method: "GET",
                       success: this.fetchCollectionsResultHandler,
                       failure: this.fetchCollectionsErrorHandler,
                       scope: this
            });
        },
	
        showCollectionPanel: function(collectionRecord)
        {
            var id = collectionRecord.get('id');
            var panel;

            if(id === 1)
            {
                panel = Ext.ComponentManager.get('pilotProjectPanel');
                
                if(panel === undefined)
                {
                    panel = new PilotProjectPanel();
                    this.infoTabPanel.add(panel);
                }
            }

            if(id === 2)
            {
                panel = Ext.ComponentManager.get('modularPromoterLibraryPanel');
                
                if(panel === undefined)
                {
                    panel = new ModularPromoterLibraryPanel();
                    this.infoTabPanel.add(panel);
                }
            }

            if(id === 3)
            {
                panel = Ext.ComponentManager.get('randomPromoterLibraryPanel');
                
                if(panel === undefined)
                {
                    panel = new RandomPromoterLibraryPanel();
                    this.infoTabPanel.add(panel);
                }
            }

            if(id === 4)
            {
                panel = Ext.ComponentManager.get('terminatorLibraryPanel');
                
                if(panel === undefined)
                {
                    panel = new TerminatorLibraryPanel();
                    this.infoTabPanel.add(panel);
                }
            }
            
            this.infoTabPanel.setActiveTab(panel);
            panel.showInfo(collectionRecord, this.parts);
        },

        showPartPanel: function(partRecord)
        {
            var panel = new PartPanel();
            this.infoTabPanel.add(panel);
            this.infoTabPanel.setActiveTab(panel);
            panel.showInfo(partRecord, this.parts);
        },
        
//        retrieveGecMeasurement: function(part)
//        {
//            var measurement = null;
//            var performance = part.performance;
//            var measurements;
//            var measurementsCount;
//
//            if(performance != undefined)
//            {
//                measurements = performance.measurements;
//                measurementsCount = measurements.length;
//                
//                for(var i = 0; i < measurementsCount; i += 1)
//                {
//                    if(measurements[i].type === 'GEC')
//                    {
//                        measurement = measurements[i];
//                    }
//                }
//
//            }
//            
//            return measurement;
//        },
        
        // REFACTOR: Place this function in a utility class
//        retrieveMeasurement: function(part)
//        {
//            var measurement;
//            var performance = part.performance;
//            var measurements;
//            var measurementsCount;
//            var bgeMeasurements = [];
//            var maxMeasurement;
//
//            if(performance != undefined)
//            {
//                measurements = performance.measurements;
//                measurementsCount = measurements.length;
//                
//                for(var i = 0; i < measurementsCount; i += 1)
//                {
//                    if(measurements[i].type === 'GEC')
//                    {
//                        //measurement = measurements[i];
//                        bgeMeasurements.push(measurements[i]);
//                    }
//                }
//
//                if(bgeMeasurements.length > 1)
//                {
//                    bgeMeasurements.sort(
//                        function(a,b)
//                        {
//                            return a.value - b.value;
//                        }
//                    );
//
//                    maxMeasurement = bgeMeasurements.pop();
//                    measurement = {label: 'Maximum ' + maxMeasurement.label, unit: maxMeasurement.unit, value: maxMeasurement.value};
//                }
//                else
//                {
//                    if(bgeMeasurements.length === 1)
//                    {
//                        measurement = bgeMeasurements[0];
//                    }
//                    else
//                    {
//                        measurement = {label: 'Unavailable', unit: 'None', value: 0};
//                    }
//                }
//            }
//            else
//            {
//                measurement = {label: 'Unavailable', unit: 'None', value: 0};
//            }
//            
//            return measurement;
//        },
    
    //******************
    //
    //  Event Handlers
    //
    //******************

    collectionsGridRowSelectHandler: function(selectModel, rowIndex, record)
    {
        var id = record.get('id');
        var promoterStore = this.promoterGridPanel.getStore();
        var terminatorStore = this.terminatorGridPanel.getStore();
        promoterStore.clearFilter(false);
        terminatorStore.clearFilter(false);

        promoterStore.filter([
        {
            property     : 'collectionId',
            value        : id,
            anyMatch     : false,
            exactMatch   : true
        }]);
    
        terminatorStore.filter([
        {
            property     : 'collectionId',
            value        : id,
            anyMatch     : false,
            exactMatch   : true
        }]);

        var collectionName = record.get('name');
        this.partsToolbarText.setText(collectionName + ' Parts');
        this.showCollectionPanel(record);
    },
    
    promoterGridRowSelectHandler: function(selectModel, rowIndex, record)
    {
//        var partID = record.get("displayId");
//        var description = record.get('description');
//        var relationRecord = null;
//        var constructID = null;
//        var constructRecord = null;
//        var constructRecords = null;
//        var constructRecordsForDisplay = [];
//        var relationPartID = null;
//        var relationsCount = this.constructPartStore.getCount();

//        for(var i = 0; i < relationsCount; i += 1)
//        {
//            relationRecord = this.constructPartStore.getAt(i);
//            relationPartID = relationRecord.get("partID");
//
//            if(relationPartID.toUpperCase() === partID.toUpperCase())
//            {
//                    constructID = relationRecord.get("constructID");
//                    constructRecords = this.constructStore.query('biofab_id', new RegExp(constructID), false, false, true);
//                    constructRecord = constructRecords.itemAt(0);
//
//                    if(constructRecord !== null && constructRecord !== undefined)
//                    {
//                        constructRecordsForDisplay.push(constructRecord);
//                    }
//            }
//        }
//
//        if(constructRecordsForDisplay.length > 0)
//        {
//            this.constructsGridPanel.getStore().removeAll();
//            this.constructsGridPanel.getStore().add(constructRecordsForDisplay);
//            this.constructsLabel.setText('Constructs with ' + partID);
//        }
//        else
//        {
//            Ext.Msg.alert('Data Access Client', 'No construct has ' + description);
//        }

        this.showPartPanel(record); 
    },
    
    terminatorGridRowSelectHandler: function(selectModel, rowIndex, record)
    {
        this.showPartPanel(record);
    },
	
//        constructsGridRowSelectHandler: function(selectModel, rowIndex, record)
//	{
//	    var biofabID = record.get("biofab_id");
//            var id = record.get('id');
//
////            if(id === 2)
////            {
////                Ext.Msg.alert('Modular Promoter Library', 'At this time, only the promoter sequences are available for the constructs in the Modular Promoter Library.\n'+
////                'The complete sequence with annotations will be available in an upcoming release of the Data Access Client.');
////            }
////
////            if(id === 3)
////            {
////                Ext.Msg.alert('Random Promoter Library', 'At this time, only the promoter sequences are available for the constructs in the Random Promoter Library.\n'+
////                'The complete sequence with annotations will be available in an upcoming release of the Data Access Client.');
////            }
////
////            if(id === 4)
////            {
////                Ext.Msg.alert('Terminator Library', 'At this time, only the terminator sequences are available for the constructs in the Terminator Library.\n'+
////                'The complete sequence with annotations will be available in an upcoming release of the Data Access Client.');
////            }
//
//	    this.showDatasheet(biofabID);
//	},

//        constructStoreForDisplayLoadHandler: function(store, records, options)
//        {
//            if(this.constructStore === null)
//            {
//               this.constructStore = new ConstructStore();
//               this.constructStore.on('load', this.constructStoreLoadHandler, this);
//            }
//            
//            this.constructStore.load({callback: this.constructStoreLoadHandler, scope:this, add:false});
//        },
	
//	constructStoreLoadHandler: function(store, records, options)
//	{
//            var countA = this.constructStore.getCount();
//            var countB = this.constructsGridPanel.getStore().getCount();
//            this.constructLoadCount += 1;
//
//            if(countA !== countB && this.constructLoadCount < 10 && countA === 0)
//            {
//               this.constructStore.load({callback: this.constructStoreLoadHandler, scope:this, add:false});
//            }
//	},

        collectionsGridExportButtonClickHandler: function(button, event)
        {
            var exportWindow = window.open(WEB_SERVICE_BASE_URL + 'collections?format=json',"Collections","width=640,height=480");
            exportWindow.scrollbars.visible = true;
            exportWindow.alert("Use File/Save As in the menu bar to save this document.");
        },

        partsExportButtonHandler: function()
        {
            var exportWindow = window.open(WEB_SERVICE_BASE_URL + 'parts?format=csv',"Parts","width=640,height=480");
            exportWindow.scrollbars.visible = true;
            exportWindow.alert("Use File/Save As in the menu bar to save this document.");
        },

//        constructsGridExportButtonClickHandler: function(button, event)
//        {
//            var exportWindow = window.open(WEB_SERVICE_BASE_URL + 'constructs?format=csv',"Constructs","width=640,height=480");
//            exportWindow.scrollbars.visible = true;
//            exportWindow.alert("Use File/Save As in the menu bar to save this document.");
//        },

        showAllPartsButtonHandler:function()
        {
            Ext.getCmp('promoterGridPanel').getStore().clearFilter(false);
            Ext.getCmp('terminatorGridPanel').getStore().clearFilter(false);
            Ext.getCmp('partsToolbarText').setText('Parts');
        },

//        showAllConstructsButtonClickHandler: function(button, event)
//        {
//            this.constructsGridPanel.getStore().clearFilter();
//            this.repopulateConstructStore();
//        },

        //Refactor!!!
//        repopulateConstructStore:function()
//        {
//            var record = null;
//            var constructRecordsForDisplay = [];
//            var count = this.constructStore.getCount();
//
//            for(var i = 0; i < count; i += 1)
//            {
//                record = this.constructStore.getAt(i);
//                constructRecordsForDisplay.push(record);
//            }
//
//            this.constructsGridPanel.getStore().removeAll();
//            this.constructsGridPanel.getStore().add(constructRecordsForDisplay);
//            this.constructsLabel.setText('Constructs');
//        },

        fetchCollectionsResultHandler: function(response, opts)
        {
            var collections = Ext.JSON.decode(response.responseText, true);
            var store = Ext.data.StoreManager.lookup('collectionStore');
            store.loadData(collections, false);

            // Temporary
            var index = store.find('id', '1', 0, false, false, true);
            store.removeAt(index);

            var collectionRecord = store.getAt(0);
            this.showCollectionPanel(collectionRecord);
        },
        
        fetchCollectionsErrorHandler: function(response, opts)
        {
            Ext.Msg.alert('Fetch Collections', 'There was an error while attempting to fetch the collections. Please reload the Data Access Client.\n' + 'Error: ' + response.responseText);
        },

        //TODO Refactor!!!
        fetchPartsResultHandler: function(response, opts)
        {
            var partsForStore = [];
            var terminators = [];
            var terminator;
            var part;
            var partForStore;
            var partsCount;
            var measurement;
            var performance;
            var measurements;
            var measurementsCount;
 
            if(response.responseText.length > 0)
            {
                this.parts = Ext.JSON.decode(response.responseText, true);
                partsCount = this.parts.length;

                for(var i = 0; i < partsCount; i += 1)
                {
                    part = this.parts[i];
                    
                    // Temporary Filter
                    if(part.type === 'promoter' && part.collectionID !== 1)
                    {
                        performance = part.performance;
                        
                        if(performance != undefined)
                        {
                            measurements = performance.measurements;
                            measurementsCount = measurements.length;

                            for(var j = 0; j < measurementsCount; j += 1)
                            {
                                if(measurements[j].type === 'GEC')
                                {
                                    measurement = measurements[j];
                                    partForStore = {
                                        collectionId: part.collectionID,
                                        displayId: part.displayID,
                                        type: part.type,
                                        description: part.description,
                                        dnaSequence: part.dnaSequence.nucleotides,
                                        geneExpressionPerCell: measurement.value,
                                        geneExpressionPerCellSD: measurement.standardDeviation,
                                        constructId: measurement.constructId
                                    }
                                    partsForStore.push(partForStore);
                                }
                            }
                        }
                    }
                    
                    if(part.type === 'terminator')
                    {
                        performance = part.performance;
                        
                        if(performance != undefined)
                        {
                            measurements = performance.measurements;
                            measurementsCount = measurements.length;

                            for(var k = 0; k < measurementsCount; k += 1)
                            {
                                if(measurements[k].type === 'TE')
                                {
                                    measurement = measurements[k];
                                    terminator = {
                                        collectionId: part.collectionID,
                                        displayId: part.displayID,
                                        type: part.type,
                                        description: part.description,
                                        dnaSequence: part.dnaSequence.nucleotides,
                                        terminationEfficiency: measurement.value,
                                        standardDeviation: measurement.standardDeviation,
                                        constructId: measurement.constructId
                                    }
                                    terminators.push(terminator);
                                }
                            }
                        }
                    }
                }
                
                this.promoterGridPanel.getStore().loadData(partsForStore, false);
                this.terminatorGridPanel.getStore().loadData(terminators, false);
                this.fetchCollections();
            }
            else
            {
                  Ext.Msg.alert('Fetch Parts', 'There was an error while attempting to fetch the parts. Please reload the Data Access Client.\n' + 'Error: ' + response.responseText);
            }
        },

        fetchPartsErrorHandler: function(response, opts)
        {
            Ext.Msg.alert('Fetch Parts', 'There was an error while attempting to fetch the parts. Please reload the Data Access Client.\n' + 'Error: ' + response.responseText);
        }
});
