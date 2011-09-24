/*
 *
 * Developed by:
 * 
 *  Cesar A. Rodriguez
 * 
 */

Ext.define('RandomPromoterLibraryPanel',
{
    extend: 'Ext.panel.Panel',
    id: 'randomPromoterLibraryPanel',
    title: 'Random Promoter Library',
    layout: 'absolute',
    tpl: '',
    closable: true,
    autoScroll: true,
    closeAction: 'destroy',
    
    collectionRecord: null,
    parts: null,
    designPanel: null,
    descriptionTextArea: null,
    performancePanel: null,

    constructor: function() {
        this.items = [
            {
                xtype: 'panel',
                title: '',
                height: 800,
                layout: 'border',
                width: 600,
                itemId: 'centerPanel',
                x: 25,
                y: 25,
                floating: false,
                shadowOffset: 6,
                autoShow: true,
                draggable: false,
                items: [
                    {
                        xtype: 'panel',
                        itemId: 'designPanel',
                        title: 'Random Promoter Library Design',
                        layout: 'fit',
                        region: 'north',
                        split: true,
                        height:250,
                        items: [
                            {
                                xtype: 'textarea',
                                itemId: 'descriptionTextArea'
                            },
                            
                        ]
                    },
                    {
                        xtype: 'panel',
                        title: 'Random Promoter Library Performance',
                        itemId: 'performancePanel',
                        layout: 'auto',
                        height: 450,
                        region:'center',
                        split: true
                    },
                    {
                        xtype:'panel',
                        title: 'Notes',
                        itemId: 'notesPanel',
                        layout: 'fit',
                        height: 100,
                        region: 'south',
                        split: true,
                        items:[
                            {
                                xtype: 'textarea',
                                value: 'Each bar indicates the performance of a part in the library.\n' +
                                       'Hover the mouse over a bar to see the identifier of a part.\n',
                                hidden: false
                            }
                        ]

                    }
                ]
            }
        ];
        
        this.callParent();
        
        this.designPanel = this.getComponent('centerPanel').getComponent('designPanel');
        this.descriptionTextArea = this.designPanel.getComponent("descriptionTextArea");
        this.performancePanel = this.getComponent('centerPanel').getComponent('performancePanel');
    },
   
    //
    //  Public Methods
    //
    
    showInfo: function(collectionRecord, parts)
    {
            var description = null;
            this.collectionRecord = collectionRecord;
            this.parts = parts;
            description = collectionRecord.get('description');
            this.descriptionTextArea.setValue(description);
            this.generateBarChart();
    },

    generateBarChart: function()
    {
        var newStore;
        var partPerformances;

        if(this.collectionRecord !== null && this.parts !== null)
        {
            partPerformances = this.generatePartPerformances(this.collectionRecord, this.parts);

            newStore = new Ext.data.Store({
                model: 'PartPerformance',
                data : partPerformances
            });

            var element = this.performancePanel.getEl();

            var barChart = Ext.create('Ext.chart.Chart',
                {
                    theme: 'Category1',
                    width: 600,
                    height: 400,
                    renderTo: element.dom,
                    animate: false,
                    store: newStore,
//                    legend:
//                        {
//                            position: 'bottom'
//                        },
                    axes: [
                        {
                          type: 'Numeric',
                          position: 'left',
                          fields: ['value'],
                          label: {
                              renderer: Ext.util.Format.numberRenderer('0,0'),
                              font: '11px Arial'
                          },
                          title: 'Mean Fluorescence per Cell (AU)',
                          grid: true,
                          minimum: 0,
                          labelTitle: {font: '14px Arial'}
                        }
//                        {
//                          type: 'Category',
//                          position: 'bottom',
//                          fields: ['biofabId'],
//                          title: 'Modular Promoters',
//                          minimum: 0,
//                          labelTitle: {font: '12px Arial'},
//                          label: {display: 'none'},
//                          renderer: function(v) { return ''; }
//                          //majorTickSteps: 50
//                          //calculateCategoryCount: true
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
                            }
                        }
                    ]
                }
            );

            this.performancePanel.removeAll(true);
            this.performancePanel.add(barChart);
        }
        else
        {
          Ext.Msg.alert('Part Performance', 'There is an error. The part performance bar chart can not be generated.');
        }
    },

    generatePartPerformances: function(collectionRecord, parts)
    {
        var part;
        var partPerformances = [];
        var partCount;
        var measurement;
        var measurements;
        var measurementsCount;
        var selectedMeasurements = [];
        var maxMeasurement;
        var collectionId;

        partCount = parts.length;
        collectionId = collectionRecord.get('id');

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

                            if(measurement.type === 'MFC')
                            {
                                selectedMeasurements.push(
                                    {
                                        biofabId: part.displayID,
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
    }
});
