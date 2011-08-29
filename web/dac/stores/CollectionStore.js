/*
 *
 *
 *
 */

CollectionStore = Ext.extend(Ext.data.JsonStore, {
    constructor: function(cfg) {
        cfg = cfg || {};
        CollectionStore.superclass.constructor.call(this, Ext.apply({
            storeId: 'collectionStore',
            //url: '../collections?format=json',
            autoLoad: false,
            fields: [
                {
                    name: 'id',
                    allowBlank: false,
                    type: 'int'
                },
                {
                    name: 'biofabID',
                    allowBlank: false,
                    type: 'string'
                },
                {
                    name: 'chassis',
                    allowBlank: false,
                    type: 'string'
                },
                {
                    name: 'name',
                    allowBlank: false,
                    type: 'string'
                },
                {
                    name: 'version',
                    allowBlank: false,
                    type: 'string'
                },
                {
                    name: 'releaseStatus',
                    allowBlank: false,
                    type: 'string'
                },
                {
                    name: 'releaseDate',
                    allowBlank: false,
                    type: 'string'
                },
                {
                    name: 'description',
                    allowBlank: false,
                    type: 'string'
                }
            ]
        }, cfg));
    }
});
new CollectionStore();