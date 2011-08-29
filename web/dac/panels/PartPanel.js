/*
 *
 * Developed by:
 * 
 *  Cesar A. Rodriguez
 * 
 */

Ext.define('PartPanel',
{
    extend: 'Ext.panel.Panel',
    title: 'Part',
    layout: 'absolute',
    closable: true,
    autoScroll: true,
    closeAction: 'destroy',
    
    //Subcomponents
    datasheetPanel: null,
    designPanel: null,
    partDesignPanel: null,
    constructDesignPanel: null,
    constructDesignExportButton: null,
    constructDesignPanelText: null,
    performancePanel: null,
    performancePlotPanel: null,
    
    //Data Members
    partRecord: null,
    constructId: null,
    parts: null,

    constructor: function() {
        this.items = [
            {
                xtype: 'panel',
                itemId: 'datasheetPanel',
                title: '',
                height: 1300,
                width: 600,
                layout: 'border',
                x: 25,
                y: 25,
                floating: false,
                shadow: false,
                shadowOffset: 6,
                autoShow: true,
                draggable: false,
                items: [
                    {
                        xtype: 'panel',
                        itemId: 'designPanel',
                        title: '',
                        layout: 'border',
                        region: 'center',
                        height: 700,
                        items: [
                            {
                                xtype: 'panel',
                                itemId: 'partDesignPanel',
                                height: 75,
                                layout: 'fit',
                                split: true,
                                region: 'center',
                                tbar: {
                                    xtype: 'toolbar',
                                    itemId: 'partDesignToolbar',
                                    height: 25,
                                    items: [
                                        {
                                            xtype: 'tbtext',
                                            itemId: 'partDesignLabel',
                                            html: '<b>Part DNA Sequence</b>'
                                        },
                                        {
                                            xtype: 'tbfill'
                                        }
                                    ]
                                },
                                items:[
                                    {
                                        xtype: 'textarea',
                                        itemId: 'sequenceTextArea',
                                        readOnly: true
                                    }
                                ]
                            },
                            {
                                xtype: 'panel',
                                itemId: 'constructDesignPanel',
                                layout: 'fit',
                                split: true,
                                region: 'south',
                                height: 600,
                                tbar: {
                                    xtype: 'toolbar',
                                    itemId: 'constructDesignPanelToolbar',
                                    items: [
                                        {
                                            xtype: 'tbtext',
                                            html: '<b>Part Characterization Construct</b>',
                                            tooltip: 'Construct used for characterizing the part.'
                                        },
                                        {
                                            xtype: 'tbfill'
                                        },
                                        {
                                            xtype: 'tbtext',
                                            itemId: 'constructDesignPanelText',
                                            text: 'Fetching Design...',
                                            hidden: true
                                        },
                                        {
                                            xtype: 'tbfill'
                                        },
                                        {
                                            xtype: 'button',
                                            itemId: 'constructDesignExportButton',
                                            text: 'Export',
                                            tooltip: 'Export the construct design in Genbank format.'
                                        }
                                    ]
                                },
                                items:[]
                            }
                        ]
                    },
                    {
                        xtype: 'panel',
                        itemId: 'performancePanel',
                        title: 'Performance',
                        layout: 'border',
                        split: true,
                        region: 'south',
                        height: 600,
                        items:[
                            {
                                xtype:'panel',
                                itemId: 'performancePlotPanel',
                                layout: 'absolute',
                                height: 500,
                                region: 'center',
                                split: true,
                                items:[]

                            },
                            {
                                xtype:'panel',
                                itemId: 'performanceNotesPanel',
                                title: 'Notes',
                                layout: 'fit',
                                height: 100,
                                region: 'south',
                                split: true,
                                items:[
                                    {
                                        xtype: 'textarea',
                                        itemId: 'performanceNotesTextArea',
                                        hidden: false
                                    }
                                ]

                            }
                        ]
                    }
                ]
            }
        ];
        
        this.callParent();
        
        this.datasheetPanel = this.getComponent('datasheetPanel');
        this.designPanel = this.datasheetPanel.getComponent('designPanel');
        this.partDesignPanel = this.designPanel.getComponent('partDesignPanel')
        this.constructDesignPanel = this.designPanel.getComponent('constructDesignPanel');
        this.constructDesignExportButton = this.constructDesignPanel.getComponent('constructDesignPanelToolbar').getComponent('constructDesignExportButton');
        this.constructDesignPanelText = this.constructDesignPanel.getComponent('constructDesignPanelToolbar').getComponent('constructDesignPanelText');
        this.constructDesignExportButton.setHandler(this.constructDesignExportButtonHandler, this);
        
        this.performancePanel = this.datasheetPanel.getComponent('performancePanel');
        this.performancePlotPanel = this.performancePanel.getComponent('performancePlotPanel');
    },
   
    //
    //  Public Methods
    //
    
    showInfo: function(partRecord, parts)
    {
            var dnaSequence = null;
            var biofabID = null;
            
            this.partRecord = partRecord;
            this.parts = parts;
            biofabID = partRecord.get('displayId');
            this.setTitle(biofabID);
            dnaSequence = partRecord.get('dnaSequence');
            this.partDesignPanel.getComponent('partDesignToolbar').getComponent('partDesignLabel').setText('<b>DNA Sequence for ' + biofabID + '</b>');
            this.partDesignPanel.getComponent('sequenceTextArea').setValue(dnaSequence);
            var collectionId = this.partRecord.get('collectionId');
            this.constructId = this.partRecord.get('constructId');
            
            
            //TODO Deal with null constructId
            this.fetchConstructDesign(this.constructId);

            //Temporary patch till I fix the problem with the Pilot Project
            if(collectionId !== 1)
            {
                this.generateBarChart(this.partRecord, this.parts);
            }
            else
            {
                this.performancePanel.add(
                    {
                        xtype: 'label',
                        text: 'Performance data for Pilot Project parts will be available in an upcoming release of the Data Access Client.'
                    }
                );
                //this.performancePanel.doLayout();
            }
    },
    
    fetchConstructDesign:function(constructID)
    {
        this.constructDesignPanelText.setVisible(true);
        Ext.Ajax.request({
                   url: WEB_SERVICE_BASE_URL + 'constructs',
                   method: "GET",
                   success: this.fetchConstructDesignResultHandler,
                   failure: this.fetchConstructDesignErrorHandler,
                   params: {
                                id: constructID,
                                format: 'insd'
                            },
                   scope: this
        });
    },
    
    // Refactor!!!
    generateBarChart: function(partRecord, parts)
    {
        var newStore;
        var partPerformances;
        var collectionId;
        var axisTitle;
        
        if(partRecord !== null && this.parts !== null)
        {
            collectionId = partRecord.get('collectionId');
            
            if(collectionId === 4)
            {
                axisTitle = 'Termination Efficiency (%)';
            }
            else
            {
                axisTitle = 'Gene Expression per Cell (AU)';
            }
            
            partPerformances = this.generatePartPerformances(partRecord, parts);

            newStore = new Ext.data.Store({
                model: 'PartPerformance',
                data : partPerformances
            });

            var barChart = Ext.create('Ext.chart.Chart',
                {
                    theme: 'Category1',
                    width: 600,
                    height: 400,
                    //renderTo: element.dom,
                    animate: false,
                    store: newStore,
                    axes: [
                        {
                          type: 'Numeric',
                          position: 'left',
                          fields: ['value'],
                          label: {
                              renderer: Ext.util.Format.numberRenderer('0,0'),
                              font: '11px Arial'
                          },
                          title: axisTitle,
                          grid: true,
                          minimum: 0,
                          labelTitle: {font: '14px Arial'}
                        },
//                        {
//                          type: 'Category',
//                          position: 'bottom',
//                          fields: ['biofabID'],
//                          title: 'Part',
//                          minimum: 0,
//                          labelTitle: {font: '12px Arial'},
//                          label: {
//                              font: '11px Arial',
//                              rotate: {degrees: 90}
//                          },
//                          calculateCategoryCount: true
//                        }
                    ],
                    series: [
                        {
                            type: 'column',
                            axis: 'left',
                            xField: 'biofabId',
                            yField: 'value',
                            highlight: false,
                            style: {opacity: 1.0},
                            //gutter: 5,
                            tips: {
                              trackMouse: true,
                              width: 120,
                              height: 28,
                              renderer: function(storeItem, item) {
                                this.setTitle('Part: ' + storeItem.get('biofabId'));
                              }
                            },
                            renderer: function(sprite, record, attr, index, store)
                                {
                                    //var biofabId = record.get('biofabId');
                                    //var partPanel = Ext.Container.getComponent('partPanel');
                                    var isSelectedPart = record.get('isSelectedPart');

                                    if(isSelectedPart)
                                    {
                                        var color = 'rgb(255, 0, 0)';
                                        return Ext.apply(attr, {fill: color});
                                    }
                                    else
                                    {
                                        return Ext.apply(attr);
                                    }

//                                    if(index === 10)
//                                    {
//                                        var color = 'rgb(255, 0, 0)';
//                                        return Ext.apply(attr, {fill: color});
//                                    }
//                                    else
//                                    {
//                                        return Ext.apply(attr);
//                                    }
                                }

//                            label: {
//                                display: 'insideEnd',
//                                field: 'biofabId',
//                                renderer: Ext.util.Format.format,
//                                orientation: 'vertical',
//                                color: '#333',
//                               'text-anchor': 'middle'
//                            }
                        }
                    ]
                }
            );

            this.performancePlotPanel.add(barChart);
            this.performancePlotPanel.doLayout();
            this.displayNotes();
        }
        else
        {
          Ext.Msg.alert('Part Performance', 'There is an error. The part performance bar chart can not be generated.');
        }
    },

    // Refactor!!!
    generatePartPerformances: function(partRecord, parts)
    {
        var part;
        var partCollection = [];
        var partPerformances = [];
        var partCount;
        var measurement;
        var performance;
        var measurements;
        var measurementsCount;
        var selectedMeasurements = [];
        var maxMeasurement;
        var collectionId;
        var selectedMeasurement;
        var selectedPartBiofabId;
        var isSelected;
        var measurementType;

        selectedPartBiofabId = partRecord.get('displayId')
        partCount = this.parts.length;
        collectionId = partRecord.get('collectionId');
        
        if(collectionId === 4)
        {
            measurementType = 'TE';
        }
        else
        {
            measurementType = 'GEC';
        }

        for(var j = 0; j < partCount; j += 1)
        {
            part = parts[j];

            if(part.collectionID === collectionId)
            {
                if(part.performance != undefined)
                {
                    measurements = part.performance.measurements;

                    if(measurements != undefined)
                    {
                        measurementsCount = measurements.length;

                        for(var i = 0; i < measurementsCount; i += 1)
                        {
                            measurement = measurements[i];
        
                            if(measurement.type === measurementType)
                            {
                                if(part.displayID === selectedPartBiofabId)
                                {
                                    isSelected = true;
                                }
                                else
                                {
                                    isSelected = false
                                }

                                selectedMeasurements.push(
                                    {
                                        biofabId: part.displayID,
                                        isSelectedPart: isSelected ,
                                        value: measurement.value
                                    }
                                );
                            }
                        }

                        if(selectedMeasurements.length > 1)
                        {
                            selectedMeasurements.sort(
                                function(a,b)
                                {
                                    return a.value - b.value;
                                }
                            );
        
                            maxMeasurement = selectedMeasurements.pop();
                            partPerformances.push(maxMeasurement);
                        }
                        else
                        {
                            if(selectedMeasurements.length === 1)
                            {
                                partPerformances.push(selectedMeasurements[0]);
                            }
                        }
                    }
                }
            }
        }

        partPerformances.sort(
            function(a,b)
            {
                return b.value - a.value;
            }
        );
        
        return partPerformances;
    },

    displayNotes: function()
    {
        this.performancePanel.getComponent('performanceNotesPanel').getComponent('performanceNotesTextArea').setValue('Each bar indicates the performance of a part in the library.\n' +
                               'Hover the mouse over a bar to see the identifier of a part.\n' +
                               'The red bar indicates the performance of the selected part.');
    },
    
    //******************
    //
    //  Event Handlers
    //
    //******************
    
    fetchConstructDesignResultHandler: function(response, opts)
    {
        this.constructDesignPanelText.setVisible(false);
        var flash = {
                xtype: 'flash',
                url:'designviewer/DesignViewer.swf',
                flashVars:{design:response.responseText}
            };
        this.constructDesignPanel.add(flash);
        //this.constructDesignPanel.doLayout();
    },

    fetchConstructDesignErrorHandler: function(response, opts)
    {
       this.constructDesignPanelText.setVisible(false);
       this.constructDesignExportButton.setDisabled(true);
       this.constructDesignPanel.setHeight(100);
       this.datasheetPanel.setHeight(800);
       this.constructDesignPanel.add(
            {
                xtype: 'panel',
                html: 'The design of the part characterization construct will be available in an upcoming release.'
            }
       )
    },
    
    constructDesignExportButtonHandler: function()
    {
        var genbankWindow = window.open(WEB_SERVICE_BASE_URL + 'constructs' + "?id=" + this.constructId + "&format=genbank","Genbank File for " + this.constructId,"width=640,height=480");
        genbankWindow.alert("Use File/Save As in the menu bar to save this document.");
        genbankWindow.scrollbars.visible = true;
    }
});
