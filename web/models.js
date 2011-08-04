Ext.define('Plasmid', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'index', type: 'int'},
        {name: 'biofabId',  type: 'string'},
        {name: 'description', type: 'string'}
    ]
});

Ext.define('Oligo', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'index', type: 'int'},
        {name: 'biofabId',  type: 'string'},
        {name: 'description', type: 'string'},
        {name: 'dnaSequence', type: 'string'}
    ]
});