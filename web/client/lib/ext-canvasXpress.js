// icons in for this tool comes from http://prothemedesign.com/circular-icons/
// license says free for any use but no re-distribution, so please download it
// directly from that site yourself or make/choose your own icons
Ext.canvasXpress = Ext.extend(Ext.Panel, {
  showExampleData: false,
  data: false,
  options: false,
  events: false,
  contextMenu: true,
  menuTitle: 'Customize',
  showPrint: true,
  changedNodes: [],
  changedEdges: [],
  initComponent: function() {
    this.canvasId = Ext.id();
    Ext.canvasXpress.superclass.initComponent.apply(this, arguments);
    if (! this.data && this.showExampleData) {
      this.data = false;
    } else if (! this.data && !this.showExampleData){
      this.data = {};
    }
    this.resetChanges();
  },
  onRender:function() {
    Ext.canvasXpress.superclass.onRender.apply(this, arguments);
    if (this.contextMenu) {
      this.el.on({contextmenu:{scope:this, fn:this.onContextMenu, stopEvent:true}});
    }
  },
  afterRender: function() {
    Ext.canvasXpress.superclass.afterRender.apply(this, arguments);
    // Add the canvas tag
    Ext.DomHelper.append(this.body, {
      tag: 'canvas',
      id: this.canvasId,
      width: this.width || 500,
      height: this.height || 500
    });
    // first set up default events
    var events = {};
    switch(this.options.graphType) {
      case 'Network':
        this.addEvents(
          'endnodedrag','removenode','removeedge',
          'expandgroup','togglenode','togglechildren','saveallchanges',
          'updatenode','updateedge','updatenodes','updateedges',
          'updatelegend','updateorder','leftclick');
        events.enddragnode = this.endDrag.createDelegate(this);
        if(this.hasListener('leftclick'))
          events.click = function(o, e) {
            this.fireEvent('leftclick', o, e)
          }.createDelegate(this);
        if(!this.hasListener('removenode'))
          this.on('removenode', function(n, f) { f() });
        if(!this.hasListener('removeedge'))
          this.on('removeedge', function(n, f) { f() });
    }
    Ext.applyIf(this.events, events);
    // Now get the canvasXpress object
    this.canvas = new CanvasXpress(this.canvasId, this.data, this.options, this.events);
    this.canvas.highlightNode = []; // clear up the initial highlight

    if (this.canvas.version < 2) {
      var msg = 'Please download a newer version of canvasXpress at:<br>';
      msg += '<a target="blank" src="http://www.canvasXpress.org">http://www.canvasXpress.org</a><br>';
      msg += 'You are using an older version that dO NOT support all the functionality of this panel';
      Ext.MessageBox.alert('Warning', msg);
    }
    Ext.get(this.id).on('click', function(e) {
      if(e.shiftKey) this.toggleSnapshotCtrl({},e.xy);
    }, this);
    this.on('destroy', function(p) {
      if(p.snapshotCtrl) p.snapshotCtrl.close();
    });
  },
  onContextMenu: function (e, o, r) {
    if (e.browserEvent) {
      if (typeof(this.contextMenu) == 'object') {
        this.contextMenu.destroy();
      }
      this.contextMenu = new Ext.menu.Menu(this.createContextMenu(e));
      this.contextMenu.showAt(e.getXY());
      e.stopEvent();
    }
  },
  networkMenu: function(o, type, it) {
    var items = [];
    if(type == 'cs') // right click menu only
    {
      if(o && o.nodes && o.nodes[0])
      {
        var n = o.nodes[0], label = n.label || n.name || n.id;
        items.push({
          icon: this.imgDir + 'edit.png',
          text: 'Edit ' + label,
          handler: this.editNode.createDelegate(this, [n], true)
        }, {
          icon: this.imgDir + 'delete.png',
          text: 'Delete ' + label,
          scope: this,
          handler: this.deleteNode.createDelegate(this, [n])
        }, {
          icon: this.imgDir + 'cancel.png',
          text: 'Hide ' + label,
          handler: this.toggleNode.createDelegate(this, [n, true])
        }, {
          text: 'Order of ' + label,
          menu: [
            {
              icon: this.imgDir + 'bring_front.png',
              text: 'Bring to Front',
              handler: this.changeNodeOrder.createDelegate(this, [n, 'bringNodeToFront'])
            },
            {
              icon: this.imgDir + 'send_back.png',
              text: 'Send to Back',
              handler: this.changeNodeOrder.createDelegate(this, [n, 'sendNodeToBack'])
            },
            {
              icon: this.imgDir + 'bring_forward.png',
              text: 'Bring Forward',
              handler: this.changeNodeOrder.createDelegate(this, [n, 'bringNodeForward'])
            },
            {
              icon: this.imgDir + 'send_backwards.png',
              text: 'Send Backward',
              handler: this.changeNodeOrder.createDelegate(this, [n, 'sendNodeBackward'])
            }
          ]
        },
        '-', {
          icon: this.imgDir + 'add.png',
          text: 'Add Edge to ' + label,
          handler: this.editEdge.createDelegate(this, [n, 'to'], true)
        }, {
          icon: this.imgDir + 'add.png',
          text: 'Add Edge from ' + label,
          handler: this.editEdge.createDelegate(this, [n, 'from'], true)
        });
        // find the edges coming from this
        if(this.canvas.data && this.canvas.data.edges)
        {
          var eMenu = [], eMenu1 = [], en = this.canvas.nodes,
              es = this.canvas.data.edges, id = n.id;
          for(var i = 0; i < es.length; i++)
          {
            var e = es[i];
            if(e.id1 == id || e.id2 == id)
            {
              var n1 = e.id1 == id? en[e.id2] : en[e.id1], label1 = n1.label || n1.name || n1.id;
              eMenu.push({
                icon: this.imgDir + 'edit.png',
                text: label1,
                handler: this.editEdge.createDelegate(this, [e], true)
              });
              eMenu1.push({
                icon: this.imgDir + 'delete.png',
                text: label1,
                handler: this.deleteEdge.createDelegate(this, [e])
              });
            }
          }
          if(eMenu.length)
            items.push({
              text: 'Edit Edge'+(eMenu.length>1?'s':'')+ ' for ' + label,
              menu: eMenu
            }, {
              text: 'Delete Edge'+(eMenu.length>1?'s':'')+ ' for ' + label,
              menu: eMenu1
            });
        }
        if(this.canvas.hasChildren(n.id)) // add group menu
        {
          items.push('-', {
            text: (n.hideChildren? 'Expand':'Collapse') + ' Children of ' + label,
            icon: this.imgDir + 'folder_' + (n.hideChildren? 'open':'close') + '.png',
            handler: this.toggleChildren.createDelegate(this, [n], true)
          });
        }
        Ext.canvasXpress.utils.addMenu(items, n, this.nodeMenu, this);
      }
      else if(o && o.edges && o.edges[0])
      {
        var e = o.edges[0], n1 = this.canvas.nodes[e.id1], n2 = this.canvas.nodes[e.id2],
            s = (n1.label || n1.name || n1.id) + ' - ' + (n2.label || n2.name || n2.id);
        items.push({
          icon: this.imgDir + 'edit.png',
          text: 'Edit ' + s,
          handler: this.editEdge.createDelegate(this, [e], true)
        }, {
          icon: this.imgDir + 'delete.png',
          text: 'Delete ' + s,
          handler: this.deleteEdge.createDelegate(this, [e])
        });
        Ext.canvasXpress.utils.addMenu(items, e, this.edgeMenu, this);
      }
      else
      {
        var type = (o && o.edgeLegend && o.edgeLegend[0])? 'edge' :
                   (o && o.nodeLegend && o.nodeLegend[0])? 'node' :
                   (o && o.textLegend)? 'text' : null;
        if(type)
        {
          items.push({
            icon: this.imgDir + 'edit.png',
            text: 'Edit This Legend',
            handler: this.editLegend.createDelegate(this, [type, o[type + 'Legend']], true)
          },{
            icon: this.imgDir + 'delete.png',
            text: 'Delete This Legend',
            handler: this.deleteLegend.createDelegate(this, [type, o[type + 'Legend']])
          });
        }
        items.push({
            icon: this.imgDir + 'add.png',
            text: 'Add Node',
            scope: this,
            handler: this.editNode
          }, {
            icon: this.imgDir + 'add.png',
            text: 'Add Edge',
            scope: this,
            handler: this.editEdge
          });
        var al = [], el = [], l = this.canvas.data.legend;
        if(!l || !l.nodes || !l.nodes.length)
          al.push({
            icon: this.imgDir + 'add.png',
            text: 'Node Legend',
            handler: this.editLegend.createDelegate(this, ['node'], true)
          });
        else
          el.push({
            icon: this.imgDir + 'edit.png',
            text: 'Node Legend',
            handler: this.editLegend.createDelegate(this, ['node'], true)
          });
        if(!l || !l.edges || !l.edges.length)
          al.push({
            icon: this.imgDir + 'add.png',
            text: 'Edge Legend',
            handler: this.editLegend.createDelegate(this, ['edge'], true)
          });
        else
          el.push({
            icon: this.imgDir + 'edit.png',
            text: 'Edge Legend',
            handler: this.editLegend.createDelegate(this, ['edge'], true)
          });
        if(!l || !l.text || !l.text.length)
          al.push({
            icon: this.imgDir + 'add.png',
            text: 'Text Legend',
            handler: this.editLegend.createDelegate(this, ['text'], true)
          });
        else
          el.push({
            icon: this.imgDir + 'edit.png',
            text: 'Text Legend',
            handler: this.editLegend.createDelegate(this, ['text'], true)
          });
        if(al.length)
          items.push({
            text: 'Add Legend',
            menu: al
          });
        if(el.length)
          items.push({
            text: 'Edit Legend',
            menu: el
          });
        var hidden = this.canvas.getHiddenNodes(), hn = [];
        for(var i = 0; i < hidden.length; i++)
        {
          var sn = hidden[i];
          hn.push({
            icon: this.imgDir + 'eye.png',
            text: sn.label || sn.name || sn.id,
            handler: this.toggleNode.createDelegate(this, [sn, false])
          });
        }
        if(hn.length)
          items.push({
            text: 'Show Hidden Nodes',
            menu: hn
          });
        if(this.showNetworkEditItems)
        {
          items.push('-', {
            text: 'Edit Network',
            icon: this.imgDir + 'edit.png',
            scope: this,
            handler: this.editNetwork
          });
          if(this.hasUnsavedChanges() && this.hasListener('saveallchanges'))
            items.push({
              text: 'Save the Network Now',
              icon: this.imgDir + 'save.png',
              scope: this,
              handler: this.saveMap
            });
        }
        items.push('-', {
            icon: this.snapshotCtrl && !this.snapshotCtrl.hidden? this.imgDir + 'power_off.png' : this.imgDir + 'power_on.png',
            text: this.snapshotCtrl && !this.snapshotCtrl.hidden? 'Hide Snapshot Control':'Show Snapshot Control',
            scope: this,
            handler: this.toggleSnapshotCtrl
          });
        Ext.canvasXpress.utils.addMenu(items, null, this.nullMenu, this);
      }
    }
    if(items.length)
    {
      for(var i = 0; i < items.length; i++)
        it.push(items[i]);
      it.push('-');
    }
  },
  hasUnsavedChanges: function() {
    return this.changedNodes.length || this.changedEdges.length || this.legendChanged || this.orderChanged || this.networkChanged;
  },
  createContextMenu: function (e) {
    var o = this.canvas.getEventAreaData(e), items = [];
    this.clickXY = e.xy;
    if(this.menuTitle)
    {
      items.push({
        text: this.menuTitle,
        style:'font-weight:bold;margin:0px 4px 0px 27px;line-height:18px'
      });
      items.push('-');
    }
    switch(this.canvas.graphType) {
      case 'Network': this.networkMenu(o, 'cs', items);
    }
    this.addItemToMenu(items, 'General', false, this.generalMenus());
    this.addItemToMenu(items, 'Axes', false, this.axesMenus());
    this.addItemToMenu(items, 'Labels', false, this.labelMenus());
    this.addItemToMenu(items, 'Legend', false, this.legendMenus());
    this.addItemToMenu(items, 'Data', false, this.dataMenus());
    items.push({
      icon: this.imgDir + 'refresh.png',
      text: 'Reset ' + this.canvas.graphType,
      scope: this.canvas,
      handler: this.canvas.redraw
    });
    if(this.showPrint)
    {
      items.push('-');
      items.push({text: 'Print',
        icon: this.imgDir + 'print.png',
  		canvasId: this.canvasId,
  		handler: this.onPrintGraph});
    }
    return items;
  },
  // Utilities
  // Add to Menu
  addItemToMenu: function (container, text, icon, items){
    if (!icon) {
      icon = '';
    }
    if (items && items.length > 0) {
      container.push({
	text: text,
	iconCls: icon,
	menu: items
      });
    }
  },
  // Form
  addFormParameter: function (p, isText) {
    var f;
    if (isText) {
      f = new Ext.form.TextField({
	width: 80,
	iconCls: 'no-icon',
	canvasId: this.canvasId,
	name: p,
	value: this.canvas[p] ? this.canvas[p] : '',
	enableKeyEvents: true
      });
    } else {
      f = new Ext.form.NumberField({
	width: 80,
	iconCls: 'no-icon',
	canvasId: this.canvasId,
	name: p,
	value: this.canvas[p] ? this.canvas[p] : '',
	enableKeyEvents: true
      });
    }
    f.on('change', this.addFormEvent, this);
    f.on('specialkey', this.enterFormEvent, this);
    return [f];
  },
  enterFormEvent: function(f, e) {
    if (e.getKey() == e.ENTER) {
      this.addFormEvent(f, f.getValue());
      this.contextMenu.hide();
    }
  },
  addFormEvent: function(f, n, o) {
    var p = f.name;
    var w = p == 'width' ? n : false;
    var h = p == 'height' ? n : false;
    if (f.canvasId) {
      var t = Ext.getCmp(Ext.get(f.canvasId).parent('div.x-panel').id);
      if (t.canvas && t.canvas[p] != n) {
	t.canvas[p] = n;
	t.canvas.draw(w, h);
      }
    }
  },
  // Color Menu
  colorMenu: function (par) {
    var handler = this.buildColorHandler(par);
    return new Ext.menu.ColorMenu({
      width: 155,
      canvasId: this.canvasId,
      handler: handler
    });
  },
  buildColorHandler: function(par) {
    return function (cm, color) {
      var t = Ext.getCmp(Ext.get(cm.canvasId).parent('div.x-panel').id);
      if (t.canvas) {
        t.canvas[par] = t.hexToRgb(color);
        t.canvas.draw();
      }
    }
  },
  hexToRgb: function (color) {
    var r = parseInt(color.substring(0,2),16);
    var g = parseInt(color.substring(2,4),16);
    var b = parseInt(color.substring(4,6),16);
    return 'rgb('+ r + ',' + g + ',' + b + ')';
  },
  // Radio Group
  buildGroupMenu: function(par, vals, callback) {
    var m = [];
    for (var i = 0; i < vals.length; i++) {
      m.push({text: vals[i] ? vals[i] : 'false',
	      group: par,
	      checked: this.canvas[par] == vals[i] ? true : false,
	      canvasId: this.canvasId,
	      checkHandler: callback ? callback : this.clickedGroupMenu
	     });
    }
    return m;
  },
  clickedGroupMenu: function(item) {
    if (item.canvasId) {
      var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
      var p = item.text == 'false' ? false : item.text;
      if (t.canvas && t.canvas[item.group] != p) {
	t.canvas[item.group] = p;
	t.canvas.draw();
      }
    }
  },
  // Print
  onPrintGraph: function(item) {
    if (item.canvasId) {
      var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
      if (t.canvas) {
	t.canvas.print();
      }
    }
  },
  // Legend
  legendMenus: function () {
    if (this.canvas.hasLegend()) {
      var items = [{
	text: 'Show',
	iconCls: '',
	menu: this.buildGroupMenu('showLegend', [true, false])
      }];
      if (this.canvas.hasLegendProperties() && this.canvas.showLegend) {
	items.push({
	  text: 'Position',
	  iconCls: '',
	  menu: this.buildGroupMenu('legendPosition', ['bottom', 'right'])
	});
	items.push({
	  text: 'Size',
	  iconCls: '',
	  menu: this.buildGroupMenu('legendFontSize', [8, 9, 10, 11, 12, 13, 14, 15, 16])
	});
	items.push({
	  text: 'Color',
	  iconCls: '',
	  menu: this.colorMenu('legendColor')
	});
	items.push({
	  text: 'Scale Factor',
	  iconCls: '',
	  menu: this.buildGroupMenu('scaleLegendFontFactor', [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2])
	});
	items.push({
	  text: 'Boxed',
	  iconCls: '',
	  menu: this.buildGroupMenu('legendBox', [true, false])
	});
      }
      return items;
    } else {
      return false;
    }
  },
  // Data
  dataMenus: function () {
    if (this.canvas.hasData()) {
      var items = [];
      items.push({
				text: 'Transpose',
				iconCls: '',
        canvasId: this.canvasId,
				handler: this.onTranspose			
			});
      if (this.canvas.hasDataSamples()) {
	this.addItemToMenu(items, 'Samples', false, this.dataSamples());
      }
      if (this.canvas.hasDataVariables()) {
	this.addItemToMenu(items, 'Variables', false, this.dataVariables());
      }
      if (this.canvas.hasDataGroups() && this.canvas.isGroupedData) {
 	this.addItemToMenu(items, 'Groups', false, this.dataGroups());
      }
      this.addItemToMenu(items, 'Series', false, this.dataSeries());
      if (this.canvas.hasDataProperties()) {
	this.addItemToMenu(items, 'Range', false, this.dataRange());
	this.addItemToMenu(items, 'Transformation', false, this.transformations());
	items.push({
	  text: 'Error Bars',
	  iconCls: '',
	  menu: this.buildGroupMenu('showErrorBars', [true, false])
	})
      }
      return items;
    }
  },
  transformations: function () {
    var s = [];
    var smps = this.canvas.getSamples();
    for (var i = 0; i < smps.length; i++) {
      var check = smps[i].index == this.canvas.ratioReference ? true : false;
      s.push({
	group: 'ratioReference',
	text: smps[i].name,
	index: smps[i].index,
	checked: check,
	canvasId: this.canvasId,
	checkHandler: this.onDataTransform
      });
    }
    return [{
      text: 'Type',
      iconCls: '',
      menu: this.buildGroupMenu('transformType', ['log2', 'log10', 'exp2', 'exp10', 'percentile', 'zscore', 'ratio', false, 'reset', 'save'], this.onDataTransform)
    }, {
      text: 'Ratio Reference',
      iconCls: '',
      menu: s
    }, {
      text: 'Z-Score Axis',
      iconCls: '',
      menu: this.buildGroupMenu('zscoreAxis', ['samples', 'variable'], this.onDataTransform)
    }];
  },
	onTranspose: function(item) {
    if (item.canvasId) {
      var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
      if (t.canvas) {
  t.canvas.transpose();
	t.canvas.draw();
      }
    }
		
	},
  onDataTransform: function (item) {
    if (item.canvasId) {
      var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
      var p = item.group == 'ratioReference' ? item.index : item.text == 'false' ? false : item.text;
      if (t.canvas && t.canvas[item.group] != p) {
	t.canvas[item.group] = p;
	var tr = t.canvas.transformType;
	var ax = t.canvas.zscoreAxis;
	var id = t.canvas.ratioReference;
	if (tr) {
	  t.canvas.transform(tr, ax, id);
	}
	t.canvas.draw();
      }
    }
  },
  dataSamples: function () {
    var s = [];
    var smps = this.canvas.getSamples();
    for (var i = 0; i < smps.length; i++) {
      var check = smps[i].hidden ? false : true;
      s.push({
	text: smps[i].name,
	checked: check,
	canvasId: this.canvasId,
	handler: this.onSamples
      });
    }
    var g = [];
    var check;
    var annt = this.canvas.getAnnotations();
    var grp = this.canvas.getGroupingFactors();
    for (var i = 0; i < annt.length; i++) {
      check = grp.hasOwnProperty(annt[i]) ? true : false;
      g.push({
	text: annt[i],
	checked: check,
	canvasId: this.canvasId,
	handler: this.onGroup
      });
    }
    return [{
      text: 'Show',
      iconCls: '',
      menu: s
    }, {
      text: 'Group',
      iconCls: '',
      menu: g
    }, {
      text: 'Sort',
      iconCls: '',
      menu: this.dataSamplesSort()
    }];
  },
  onSamples: function (item) {
    var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
    if (t.canvas) {
      t.canvas.hideUnhideSmps(item.text);
      t.canvas.draw();
    }
  },
  onGroup: function (item) {
    var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
    if (t.canvas) {
      t.canvas.modifyGroupingFactors(item.text, item.checked);
      t.canvas.groupSamples(t.canvas.getGroupingFactors(true));
      t.canvas.draw();
    }
  },
  dataSamplesSort: function () {
    var v = [];
    var vars = this.canvas.getVariables();
    for (var i = 0; i < vars.length; i++) {
      v.push({
	text: vars[i].name,
	isVar: true,
	index: i + 1,
	checked: this.canvas.varSort == i ? true : false,
	canvasId: this.canvasId,
	handler: this.onSamplesSort
      });
    }
    var c = [];
    var annt = this.canvas.getAnnotations();
    for (var i = 0; i < annt.length; i++) {
      c.push({
	group: 'catSort',
	text: annt[i],
	category: true,
	checked: this.canvas.smpSort == annt[i] ? true : false,
	canvasId: this.canvasId,
	handler: this.onSamplesSort
      });
    }
    return [{
      text: 'By Value of Variable',
      iconCls: '',
      menu: v
    }, {
      text: 'By Annotation',
      iconCls: '',
      menu: c
    }, {
      text: 'By Name',
      iconCls: '',
      canvasId: this.canvasId,
      handler: this.onSamplesSort
    }, {
      text: 'Direction',
      iconCls: '',
      menu: this.buildGroupMenu('sortDir', ['ascending', 'descending'])
    }];
  },
  onSamplesSort: function (item) {
    var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
    var p = item.text == 'false' ? false : item.text;
    if (t.canvas && t.canvas[item.group] != p) {
      if (item.group == 'sortDir') {
	t.canvas.sortDir = item.text;
      }
      if (item.text == 'By Name') {
	t.canvas.sortIndices('smps', t.canvas.sortDir);
      } else {
	if (item.category) {
	  t.canvas.sortIndices('smps', t.canvas.sortDir, item.text);
	} else if (item.isVar) {
	  t.canvas.sortIndices('smps', t.canvas.sortDir, false, false, item.index);
	} else {
	  t.canvas.sortIndices('smps', t.canvas.sortDir);
	}
      }
      t.canvas.draw();
    }
  },
  dataGroups: function () {
    var g = [];
    var grps = this.canvas.getSamples();
    for (var i = 0; i < grps.length; i++) {
      var check = grps[i].hidden ? false : true;
      g.push({
	text: grps[i].name,
	checked: check,
	isVar: false,
	canvasId: this.canvasId,
	handler: this.onSamples
      });
    }
    return [{
      text: 'Show',
      iconCls: '',
      menu: g
    }];
  },
  dataVariables: function () {
    var items = [];
    var v = [];
    var vars = this.canvas.getVariables();
    var annt = this.canvas.getAnnotations(true);
    for (var i = 0; i < vars.length; i++) {
      var check = vars[i].hidden ? false : true;
      v.push({
	text: vars[i].name,
	checked: check,
	canvasId: this.canvasId,
	handler: this.onVariables
      });
    }
    items.push({
      text: 'Show',
      iconCls: '',
      menu: v
    })
    if (annt && this.canvas.isSegregable()) {
      var c = [];
      annt.push(false);
      for (var i = 0; i < annt.length; i++) {
	c.push({
	  group: 'segregateBy',
	  text: annt[i] == false ? 'false' : annt[i],
	  category: true,
	  checked: this.canvas.segregateBy == annt[i] ? true : false,
	  canvasId: this.canvasId,
	  handler: this.onSegregate
	});
      }
      items.push({
	text: 'Segregate',
	iconCls: '',
	menu: c
      })
      annt.pop();
    }
    items.push({
      text: 'Sort',
      iconCls: '',
      menu: this.dataVariablesSort(annt)
    })
    return items;
  },
  onVariables: function (item) {
    var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
    if (t.canvas) {
      t.canvas.hideUnhideVars(item.text);
      t.canvas.draw();
    }
  },
  onSegregate: function(item) {
    var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
    if (t.canvas) {
      if (item.text == 'false') {
	t.canvas.desegregateVariables();
      } else {
	t.canvas.segregateVariables(item.text);
      }
      t.canvas.draw();
    }
  },
  dataVariablesSort: function (annt) {
    var items = [];
    var s = [];
    var smps = this.canvas.getSamples();
    for (var i = 0; i < smps.length; i++) {
      s.push({
	group: 'sampleSort',
	text: smps[i].name,
	index: i + 1,
	isSmp: true,
	category: false,
	checked: this.canvas.smpSort == i ? true : false,
	canvasId: this.canvasId,
	handler: this.onVariablesSort
      });
    }
    var c = [];
    if (annt) {
      for (var i = 0; i < annt.length; i++) {
	c.push({
	  group: 'catSort',
	  text: annt[i],
	  category: true,
	  checked: this.canvas.varSort == annt[i] ? true : false,
	  canvasId: this.canvasId,
	  handler: this.onVariablesSort
	});
      }
    }
    items.push({
      text: 'By Value in Samples',
      iconCls: '',
      menu: s
    })
    if (c.length > 0) {
      items.push({
	text: 'By Annotation',
	iconCls: '',
	menu: c
      })
    }
    items.push({
      text: 'By Name',
      iconCls: '',
      canvasId: this.canvasId,
      handler: this.onVariablesSort
    })
    items.push({
      text: 'Direction',
      iconCls: '',
      menu: this.buildGroupMenu('sortDir', ['ascending', 'descending'])
    });
    return items;
  },
  onVariablesSort: function (item) {
    var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
    var p = item.text == 'false' ? false : item.text;
    if (t.canvas && t.canvas[item.group] != p) {
      if (item.group == 'sortDir') {
	t.canvas.sortDir = item.text;
      }
      if (item.text == 'By Name') {
	t.canvas.sortIndices('vars', t.canvas.sortDir);
      } else {
	if (item.category) {
	  t.canvas.sortIndices('vars', t.canvas.sortDir, item.text);
	} else if (item.isSmp) {
	  t.canvas.sortIndices('vars', t.canvas.sortDir, false, item.index);
	} else {
	  t.canvas.sortIndices('vars', t.canvas.sortDir);
	}
      }
      t.canvas.draw();
    }
  },
  dataRange: function () {
    var m = [];
    var axes = this.canvas.getValidAxes();
    for (var i = 0; i < axes.length; i++) {
      var l = axes[i] == 'xAxis2' ? 'X2' : axes[i].substring(0,1).toUpperCase();
      var p = this.canvas.graphType.match(/Scatter/) ? l : axes[i] == 'xAxis2' ? '2' : '';
      m.push({text: axes[i].replace('Axis', '-Axis'),
	      iconCls: '',
	      menu: [{text: 'Min',
		      menu: this.addFormParameter('setMin' + p)},
		     {text: 'Max',
		      menu: this.addFormParameter('setMin' + p)}]});
    }
    return m;
  },
  dataSeries: function () {
    var m = [];
    if (this.canvas.graphType == 'BarLine' || this.canvas.graphType.match(/Scatter/) || this.canvas.graphType == 'Pie') {
      var axes = this.canvas.getValidAxes(true);
      var objs = this.canvas.graphType == 'BarLine' ? this.canvas.getVariables() : this.canvas.getSamples();
      for (var i = 0; i < axes.length; i++) {
	var oba = this.canvas.graphType == 'BarLine' ? this.canvas.getVariablesByAxis(axes[i]) : this.canvas.getSamplesByAxis(axes[i]);
	var o = [];
	for (var j = 0; j < objs.length; j++) {
	  var check = false;
	  for (var k = 0; k < oba.length; k++) {
	    if (objs[j].name == oba[k]) {
	      check = true;
	      break;
	    }
	  }
	  if (this.canvas.graphType == 'Scatter2D' || this.canvas.graphType == 'ScatterBubble2D') {
	    o.push({text: objs[j].name,
		    checked: check,
		    canvasId: this.canvasId,
		    isVar: false,
		    handler: this.onDataSeries});
	  } else if (this.canvas.graphType == 'Scatter3D' || this.canvas.graphType == 'Pie') {
	    o.push({text: objs[j].name,
		    group: 'axis',
		    checked: check,
		    canvasId: this.canvasId,
		    isVar: false,
		    checkHandler: this.onDataSeries});
	  } else if (this.canvas.graphType == 'BarLine') {
	    o.push({text: objs[j].name,
		    checked: check,
		    canvasId: this.canvasId,
		    isVar: true,
		    handler: this.onDataSeries});
	  }
	}
	var str = axes[i].replace('Axis', '-Axis');
	if (o.length > 0) {
	  m.push({text: str,
		  iconCls: '',
		  menu: o});
	}
      }
    }
    return m;
  },
  onDataSeries: function (item) {
    var axis = item.getBubbleTarget().ownerCt.text;
    var check = item.checked;
    var isVar = item.isVar;
    var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
    if (t.canvas) {
      axis = axis.replace('-Axis', 'Axis');
      var res;
      if (isVar) {
	res = t.canvas.addRemoveVariablesInAxis(item.text, axis, check);
      } else {
	res = t.canvas.addRemoveSamplesInAxis(item.text, axis, check);
      }
      if (res) {
	Ext.MessageBox.alert('Status', res);
      } else {
	t.canvas.draw();
      }
    }
  },
  // Labels
  labelMenus: function () {
    var items = [];
    var lab = this.canvas.isGroupedData ? 'Groups' : 'Samples';
    if (this.canvas.hasDataSamples()) {
      this.addItemToMenu(items, lab, false, this.labelSamples());
    }
    if (this.canvas.hasDataVariables()) {
      this.addItemToMenu(items, 'Variables', false, this.labelVariables());
    }
    return items;
  },
  labelSamples: function () {
    var h = [];
    var smps = this.canvas.getSamples();
    var hls = this.canvas.getHighlights();
    for (var i = 0; i < smps.length; i++) {
      var check = hls.hasOwnProperty(smps[i].name) ? true : false;
      h.push({
	text: smps[i].name,
	checked: check,
	isVar: false,
	canvasId: this.canvasId,
	handler: this.onHighlight
      });
    }
    return [{
      text: 'Size',
      iconCls: '',
      canvasId: this.canvasId,
      menu: this.buildGroupMenu('smpLabelFontSize', [8, 9, 10, 11, 12, 13, 14, 15, 16])
    }, {
      text: 'Scale Factor',
      iconCls: '',
      menu: this.buildGroupMenu('scaleSmpFontFactor', [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2])			
		}, {
      text: 'Max String Length',
      iconCls: '',
      canvasId: this.canvasId,
      menu: this.addFormParameter('maxSmpStringLen')
    }, {
      text: 'Color',
      iconCls: '',
      menu: this.colorMenu('smpLabelColor')
    }, {
      text: 'Highlight',
      iconCls: '',
      menu: h
    }, {
      text: 'Highlight Color',
      iconCls: '',
      menu: this.colorMenu('smpHighlightColor')
    }];
  },
  labelVariables: function () {
    var h = [];
    var vars = this.canvas.getVariables();
    var hls = this.canvas.getHighlights(true);
    for (var i = 0; i < vars.length; i++) {
      var check = hls.hasOwnProperty(vars[i].name) ? true : false;
      h.push({
	text: vars[i].name,
	checked: check,
	isVar: true,
	canvasId: this.canvasId,
	handler: this.onHighlight
      });
    }
    return [{
      text: 'Size',
      iconCls: '',
      canvasId: this.canvasId,
      menu: this.buildGroupMenu('varLabelFontSize', [8, 9, 10, 11, 12, 13, 14, 15, 16])
    }, {
      text: 'Scale Factor',
      iconCls: '',
      menu: this.buildGroupMenu('scaleVarFontFactor', [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2])     
    }, {
      text: 'Max String Length',
      iconCls: '',
      menu: this.addFormParameter('maxVarStringLen')
    }, {
      text: 'Color',
      iconCls: '',
      menu: this.colorMenu('varLabelColor')
    }, {
      text: 'Highlight',
      iconCls: '',
      menu: h
    }, {
      text: 'Highlight Color',
      iconCls: '',
      menu: this.colorMenu('varHighlightColor')
    }];
  },
  onHighlight: function (item) {
    var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
    if (t.canvas) {
      t.canvas.modifyHighlights(item.text, item.checked, item.isVar);
      t.canvas.draw();
    }
  },
  // Axes
  axesMenus: function () {
    var items = [];
    var axes = this.canvas.getValidAxes();
    if (axes) {
      this.addItemToMenu(items, 'Font Sizes', false, this.axesFontSizes());
      this.addItemToMenu(items, 'Colors', false, this.axesColors(axes));
      this.addItemToMenu(items, 'Scale Factors', false, this.axesFontScaleFactors());
      this.addItemToMenu(items, 'Show', false, this.axesShow(axes));
      this.addItemToMenu(items, 'Properties', false, this.axesProperties(axes));
      this.addItemToMenu(items, 'Titles', false, this.axesTitles(axes));
      this.addItemToMenu(items, 'Ticks', false, this.axesTicks(axes));
      this.addItemToMenu(items, 'Transform', false, this.axesTransforms(axes));
    }
    return items;
  },
  axesFontSizes: function () {
    var items = [{
      text: 'Ticks',
      iconCls: '',
      menu: this.buildGroupMenu('axisTickFontSize', [8, 9, 10, 11, 12, 13, 14, 15, 16])
    }, {
      text: 'Titles',
      iconCls: '',
      menu: this.buildGroupMenu('axisTitleFontSize', [8, 9, 10, 11, 12, 13, 14, 15, 16])
    }];
    return items;
  },
  axesFontScaleFactors: function () {
    var items = [{
      text: 'Ticks',
      iconCls: '',
      menu: this.buildGroupMenu('scaleTickFontFactor', [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2])
    }, {
      text: 'Titles',
      iconCls: '',
      menu: this.buildGroupMenu('scaleTitleFontFactor', [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2])
    }];
    return items;
  },
  axesColors: function (axes) {
    var m = [];
    var ax = [];
    for (var i = 0; i < axes.length; i++) {
      var s = axes[i].replace('Axis', '-Axis');
      ax.push({text: s,
	       iconCls: '',
	       menu: this.colorMenu(axes[i] + 'TickColor')});
    }
    if (ax.length > 0) {
      m.push({text: 'Mesh',
	      iconCls: '',
	      menu: ax});
    }
    m.push({text: 'Ticks',
	    iconCls: '',
	    menu: this.colorMenu('axisTickColor')});
    m.push({text: 'Titles',
	    iconCls: '',
	    menu: this.colorMenu('axisTitleColor')});
    return m;
  },
  axesShow: function (axes) {
    var m = [];
    for (var i = 0; i < axes.length; i++) {
      m.push({text: axes[i].replace('Axis', '-Axis'),
	      iconCls: '',
	      menu: this.buildGroupMenu(axes[i] + 'Show', [true, false])});
    }
    return m;
  },
  axesProperties: function (axes) {
    var m = [];
    var a = [];
    m.push({text: 'Over-Extension',
	    iconCls: '',
	    menu: this.addFormParameter('axisExtension')});
    for (var i = 0; i < axes.length; i++) {
      a.push({text: axes[i].replace('Axis', '-Axis'),
	      iconCls: '',
	      menu: this.buildGroupMenu(axes[i] + 'Exact', [true, false])});
    }
    if (a.length > 0) {
      m.push({text: 'Exact',
	      iconCls: '',
	      menu: a});
    }
    return m;
  },
  axesTitles: function (axes) {
    var m = [];
    if (this.canvas.graphType.match(/Scatter/)) {
      for (var i = 0; i < axes.length; i++) {
	var s = axes[i].replace('Axis', '-Axis');
	var n = axes[i] + 'Title';
	m.push({text: s,
		iconCls: '',
		menu: this.addFormParameter(n, true)});
      }
    }
    return m;
  },
  axesTicks: function (axes) {
    var m = [];
    var n = this.axesTicksNumber(axes);
    var s = this.axesTickStyles(axes);
    if (n.length > 0) {
      m.push({text: 'Number',
              iconCls: '',
              menu: n});
    }
    if (s.length > 0) {
      m.push({text: 'Style',
	      iconCls: '',
	      menu: s});
    }
    return m;
  },
  axesTicksNumber: function (axes) {
    var m = [];
    for (var i = 0; i < axes.length; i++) {
      var s = axes[i].replace('Axis', '-Axis');
      var n = axes[i] + 'Ticks';
      m.push({text: s,
	      iconCls: '',
	      menu: this.addFormParameter(n)});
    }
    return m;
  },
  axesTickStyles: function (axes) {
    var m = [];
    if (this.canvas.graphType.match(/Scatter/)) {
      for (var i = 0; i < axes.length; i++) {
	var s = axes[i].replace('Axis', '-Axis');
	var n = axes[i] + 'TickStyle';
	m.push({text: s,
		iconCls: '',
		menu: this.buildGroupMenu(n, ['solid', 'dotted'])});
      }
    }
    return m;
  },
  axesTransforms: function (axes) {
    var m = [];
    if (this.canvas.graphType.match(/Scatter/)) {
      for (var i = 0; i < axes.length; i++) {
	m.push({text: axes[i].replace('Axis', '-Axis'),
		iconCls: '',
		menu: this.buildGroupMenu(axes[i] + 'Transform', ['log2', 'log10', 'exp2', 'exp10',
								  'percentile', false])});
      }
    }
    return m;
  },
  // General
  generalMenus: function () {
    var items = [];
    this.addItemToMenu(items, 'Colors', false, this.generalColors());
    this.addItemToMenu(items, 'Dimensions', false, this.dimensions());
    this.addItemToMenu(items, 'Fonts', false, this.font());
    this.addItemToMenu(items, 'Layout', false, this.graphLayout());
    this.addItemToMenu(items, 'Main Title', false, this.titles());
    this.addItemToMenu(items, 'Orientation', false, this.graphOrientation());
    this.addItemToMenu(items, 'Overlays', false, this.overlays());
    this.addItemToMenu(items, 'Plot', false, this.plot());
    this.addItemToMenu(items, 'Shadows', false, this.shadows());
    this.addItemToMenu(items, 'Types', false, this.graphTypes());
    return items;
  },
  generalColors: function() {
    return [{
      text: 'Background',
      iconCls: '',
      menu: this.background()
    }, {
      text: 'Foreground',
      iconCls: '',
      menu: this.foreground()
    }];
  },
  foreground: function () {
    return this.colorMenu('foreground');
  },
  background: function () {
    var m = [];
    m.push({text: 'Type',
	    iconCls: '',
	    menu: this.backgroundType()});
    if (this.canvas.backgroundType == 'gradient') {
      m.push({text: 'Colors',
	      iconCls: '',
	      menu: this.backgroundGradients()});
    } else {
      m.push({text: 'Color',
	      iconCls: '',
	      menu: this.colorMenu('background')});
    }
    return m;
  },
  backgroundType: function () {
    return this.buildGroupMenu('backgroundType', ['solid', 'gradient']);
  },
  backgroundGradients: function () {
    return [{
      text: 'Color1',
      iconCls: '',
      menu: this.colorMenu('backgroundGradient1Color')
    }, {
      text: 'Color2',
      iconCls: '',
      menu: this.colorMenu('backgroundGradient2Color')
    }];
  },
  dimensions: function () {
    return [{
      text: 'Width',
      iconCls: '',
      menu: this.addFormParameter('width')
    }, {
      text: 'Height',
      iconCls: '',
      menu: this.addFormParameter('height')
    }, {
      text: 'Margins',
      iconCls: '',
      menu: this.addFormParameter('margin')
    }];
  },
  font: function() {
    return [
      {text: 'Name',
       iconCls: '',
       menu: this.fontName()},
      {text: 'Max Size',
       iconCls: '',
       menu: this.fontSize()},
      {text: 'Auto Scale',
       iconCls: '',
       menu: this.fontAutoScale()}
    ];
  },
  fontName: function() {
    return this.buildGroupMenu('fontName', this.canvas.fonts);
  },
  fontSize: function() {
    return this.buildGroupMenu('maxTextSize', [8, 9, 10, 11, 12, 13, 14, 15, 16]);
  },
  fontAutoScale: function() {
    return this.buildGroupMenu('autoScaleFont', [true, false]);
  },
  graphLayout: function() {
    var items = [];
    if (this.canvas.layoutComb) {
      var c = 0;
      for (var i = 0; i < this.canvas.layoutRows; i++) {
	for (var j = 0; j < this.canvas.layoutCols; j++) {
	  var lab = 'Graph ' + (c + 1) + ' Weight';
	  items.push({
	    text: lab,
	    iconCls: '',
	    menu: this.addFormParameter('subGraphWeight' + c)
	  });
	  c++;
	}
      }
    }
    return items;
  },
  titles: function () {
    var items = [{
      text: 'Title',
      iconCls: '',
      menu: this.titlesTitle()
    }];
    if (this.canvas.title) {
      items.push({
	text: 'Subtitle',
	iconCls: '',
	menu: this.titlesSubTitle()
      });
    }
    return items;
  },
  titlesTitle: function () {
    var items = [{
      text: 'Text',
      iconCls: '',
      menu: this.addFormParameter('title', true)
    }];
    if (this.canvas.title) {
      items.push({
	text: 'Height',
	iconCls: '',
	menu: this.addFormParameter('titleHeight')
      });
    }
    return items;
  },
  titlesSubTitle: function () {
    var items = [{
      text: 'Text',
      iconCls: '',
      menu: this.addFormParameter('subtitle', true)
    }];
    if (this.canvas.subtitle) {
      items.push({
	text: 'Height',
	iconCls: '',
	menu: this.addFormParameter('subtitleHeight')
      });
    }
    return items;
  },
  graphOrientation: function () {
    if (this.canvas.hasOrientation()) {
      return this.buildGroupMenu('graphOrientation', ['vertical', 'horizontal']);
    } else {
      return false;
    }
  },
  overlays: function () {
    if (this.canvas.hasOrientation()) {
      var items = [];
      var o = [];
      var annt = this.canvas.getAnnotations();
      var ovls = this.canvas.getOverlays();
      var isOvl = false;
      for (var i = 0; i < annt.length; i++) {
	var check = ovls.hasOwnProperty(annt[i]) ? true : false;
	if (check) {
	  isOvl = true;
	}
	o.push({
	  text: annt[i],
	  checked: check,
	  canvasId: this.canvasId,
	  handler: this.onOverlays
	});
      }
      if (annt && annt.length > 0) {
	items.push({
	  text: 'Annotations',
	  iconCls: '',
	  menu: o
	});
	if (isOvl) {
	  items.push({
	    text: 'Width',
	    iconCls: '',
	    menu: this.addFormParameter('overlaysWidth')
	  });
	}
      }
      return items;
    } else {
      return false;
    }

  },
  onOverlays: function (item) {
    var t = Ext.getCmp(Ext.get(item.canvasId).parent('div.x-panel').id);
    if (t.canvas) {
      t.canvas.modifyOverlays(item.text, item.checked);
      t.canvas.draw();
    }
  },
  // Plot specific
  plot: function () {
    switch (this.canvas.graphType) {
      case 'Bar':
      case 'Area':
      case 'Dotplot':
      case 'Stacked':
      case 'StackedPercent':
      case 'Boxplot':
        return this.oneDGraphs();
      case 'Line':
      case 'BarLine':
        return [{
	  text: 'Configuration',
	  iconCls: '',
	  menu: this.oneDGraphs()
	}, {
	  text: 'Lines',
	  iconCls: '',
	  menu: this.lines()
	}];
      case 'Heatmap':
        var items = [{
	  text: 'Configuration',
	  iconCls: '',
	  menu: this.oneDGraphs()
	}, {
	  text: 'Heatmaps',
	  iconCls: '',
	  menu: this.heatmaps()
	}];
        this.addItemToMenu(items, 'Trees', false, this.dendrograms())
        return items;
      case 'Scatter2D':
        return this.scatter2D();
      case 'ScatterBubble2D':
        return false;
      case 'Scatter3D':
        return this.scatter3D();
      case 'Correlation':
        return this.correlation();
      case 'Venn':
        return this.venn();
      case 'Pie':
        return this.pie();
      case 'Network':
        return this.networks();
      case 'Genome':
      return this.genomeBrowser();
    }
  },
  shadows: function () {
    if (!this.canvas.isIE) {
      return [{
	text: 'Show',
	iconCls: '',
	menu: this.buildGroupMenu('showShadow', [true, false])
      }];
    } else {
      return false;
    }
  },
  // 1D graaphs
  oneDGraphs: function () {
    if (this.canvas.graphType == 'Heatmap') {
      return this.blocks()
    } else {
      var items = [];
      this.addItemToMenu(items, 'Sample Hairline', false, this.hairline());
      this.addItemToMenu(items, 'Sample Blocks', false, this.blocks());
      this.addItemToMenu(items, 'Trees', false, this.dendrograms(true))
      return items;
    }
  },
  hairline: function () {
    return [{
      text: 'Type',
      iconCls: '',
      menu: this.buildGroupMenu('smpHairline', ['solid', 'dotted', false])
    }, {
      text: 'Color',
      iconCls: '',
      menu: this.colorMenu('smpHairlineColor')
    }];
  },
  blocks: function() {
    var items = [];
    if (this.canvas.graphType != 'Heatmap') {
      items.push({
	text: 'Contrast',
	iconCls: '',
	menu: this.buildGroupMenu('blockContrast', [true, false])
      });
      if (this.canvas.blockContrast) {
	items.push({
	  text: 'Contrast Odd Colors',
	  iconCls: '',
	  menu: this.colorMenu('blockContrastOddColor')
	});
	items.push({
	  text: 'Contrast Even Colors',
	  iconCls: '',
	  menu: this.colorMenu('blockContrastEvenColor')
	});
      }
    }
    if (! this.canvas.layoutComb) {
      items.push({
	text: 'Autoextend',
	iconCls: '',
	menu: this.buildGroupMenu('autoExtend', [true, false])
      });
      if (this.canvas.autoExtend) {
	if (this.canvas.graphType != 'Heatmap') {
	  items.push({
	    text: 'Separation Factor',
	    iconCls: '',
	    menu: this.buildGroupMenu('blockSeparationFactor', [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 3, 4, 5])
	  });
	}
	items.push({
	  text: 'Width / Height Factor',
	  iconCls: '',
	  menu: this.buildGroupMenu('blockFactor', [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 3, 4, 5])
	});
      }
    }
    return items;
  },
  // Lines / BarLines
  lines: function () {
    var items = [{
      text: 'Decorations',
      iconCls: '',
      menu: this.buildGroupMenu('lineDecoration', ['dot', 'symbol', false])
    }]
    if (this.canvas.graphType != 'Barline') {
      items.push({
	text: 'Coordinate Colors in Bar / Lines',
	iconCls: '',
	menu: this.buildGroupMenu('coordinateLineColor', [true, false])
      })
    }
    return items;
  },
  // 2D Scatter
  scatter2D: function () {
    var items = [{
      text: 'Configuration',
      iconCls: '',
      menu: this.scatterParameters()
    }, {
      text: 'Indicators',
      iconCls: '',
      menu: this.scatterIndicators()
    }, {
      text: 'Plot as bars',
      iconCls: '',
      menu: this.buildGroupMenu('barPlot', [true, false])
    }];
    if (this.canvas.barPlot) {
      items.push({
	text: 'Bar width',
	iconCls: '',
	menu: this.addFormParameter('barPlotWidth')
      });
    }
    if (this.canvas.hasDecorations()) {
      items.push({
	text: 'Decorations',
	iconCls: '',
	menu: this.scatter2DDecorations()
      });
    }
    return items;
  },
  scatter2DDecorations: function () {
    var items = [{
      text: 'Show',
      iconCls: '',
      menu: this.buildGroupMenu('showDecorations', [true, false])
    }];
    if (this.canvas.showDecorations) {
      items.push({
	text: 'Position',
	iconCls: '',
	menu: this.buildGroupMenu('decorationsPosition', ['right', 'bottom'])
      });
      items.push({
	text: 'Size',
	iconCls: '',
	menu: this.buildGroupMenu('decorationFontSize', [8, 9, 10, 11, 12, 13, 14, 15, 16])
      });
      items.push({
	text: 'Color',
	iconCls: '',
	menu: this.colorMenu('decorationsColor')
      })
      items.push({
	text: 'Scale Factor',
	iconCls: '',
	menu: this.buildGroupMenu('scaleDecorationFontFactor', [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2])
      });
    }
    return items;
  },
  scatterIndicators: function () {
    var items = [{
      text: 'Show',
      iconCls: '',
      menu: this.buildGroupMenu('showIndicators', [true, false])
    }];
    if (this.canvas.showIndicators) {
      items.push({
	text: 'Position',
	iconCls: '',
	menu: this.buildGroupMenu('indicatorsPosition', ['right', 'bottom'])
      });
    }
    return items;
  },
  // 3D Scatter
  scatter3D: function () {
    return [{
      text: 'Rotation',
      iconCls: '',
      menu: this.scatter3DRotate()
    }, {
      text: 'Configuration',
      iconCls: '',
      menu: this.scatterParameters()
    }, {
      text: 'Indicators',
      iconCls: '',
      menu: this.scatterIndicators()
    }];
  },
  scatterParameters: function () {
    var annt = this.canvas.getAnnotations(true);
    var smps = this.canvas.getSamples();
    for (var i = 0; i < smps.length; i++) {
      annt.push(smps[i].name);
    }    
    annt.push('variable');
    annt.push(false);
    return [{
      text: 'Color By',
      iconCls: '',
      menu: this.buildGroupMenu('colorBy', annt)
    }, {
      text: 'Shape By',
      iconCls: '',
      menu: this.buildGroupMenu('shapeBy', annt)
    }, {
      text: 'Size By',
      iconCls: '',
      menu: this.buildGroupMenu('sizeBy', annt)
    }];
  },
  scatter3DRotate: function () {
    return [{
      text: 'X-Axis',
      iconCls: '',
      menu: this.addFormParameter('xRotate')
    }, {
      text: 'Y-Axis',
      iconCls: '',
      menu: this.addFormParameter('yRotate')
    }, {
      text: 'Z-Axis',
      iconCls: '',
      menu: this.addFormParameter('zRotate')
    }];
  },
  // Correlation
  correlation: function () {
    return [{
      text: 'Anchor',
      iconCls: '',
      menu: this.correlationAnchor()
    }, {
      text: 'Axis',
      iconCls: '',
      menu: this.buildGroupMenu('correlationAxis', ['samples', 'variables'])
    }, {
      text: 'Heatmap',
      iconCls: '',
      menu: this.heatmaps()
    }];
  },
  correlationAnchor: function () {
    return [{
      text: 'Show',
      iconCls: '',
      menu: this.buildGroupMenu('correlationAnchorLegend', [true, false])
    }, {
      text: 'Width',
      iconCls: '',
      menu: this.addFormParameter('correlationAnchorLegendAlignWidth')
    }];
  },
  // Heatmap
  heatmaps: function () {
    return [{
      text: 'Bins',
      iconCls: '',
      menu: this.addFormParameter('bins')
    }, {
      text: 'Indicator Width',
      iconCls: '',
      menu: this.addFormParameter('indicatorWidth')
    }, {
      text: 'Scheme',
      iconCls: '',
      menu: this.buildGroupMenu('heatmapType', ['blue', 'blue-green', 'blue-red', 'green', 'green-blue', 'green-red', 'red', 'red-blue', 'red-green'])
    }];
  },
  // Trees
  dendrograms: function (justSamples) {
    if (this.canvas.hasDendrograms) {
      var items = [];
      items.push({
	text: 'Samples',
	iconCls: '',
	menu: this.dendrogramSamples()
      });
      if (!justSamples) {
	items.push({
	  text: 'Variables',
	  iconCls: '',
	  menu: this.dendrogramVariables()
	});
      }
      if (this.canvas.showSmpDendrogram || this.canvas.showVarDendrogram) {
	items.push({
	  text: 'Height',
	  iconCls: '',
	  menu: this.addFormParameter('dendrogramSpace')
	});
	items.push({
	  text: 'Hang',
	  iconCls: '',
	  menu: this.buildGroupMenu('dendrogramHang', [true, false])
	});
      }
      return items;
    } else {
      return false;
    }
  },
  dendrogramSamples: function () {
    var items = [{
      text: 'Show',
      iconCls: '',
      menu: this.buildGroupMenu('showSmpDendrogram', [true, false])
    }];
    if (this.canvas.showSmpDendrogram) {
      var o = this.canvas.graphOrientation == 'vertical' ? ['top', 'bottom'] : ['left', 'right'];
      items.push({
	text: 'Position',
	iconCls: '',
	menu: this.buildGroupMenu('smpDendrogramPosition', o)
      });
    }
    return items;
  },
  dendrogramVariables: function () {
    var items = [{
      text: 'Show',
      iconCls: '',
      menu: this.buildGroupMenu('showVarDendrogram', [true, false])
    }];
    if (this.canvas.showVarDendrogram) {
      items.push({
	text: 'Position',
	iconCls: '',
	menu: this.buildGroupMenu('varDendrogramPosition', ['top', 'bottom'])
      });
    }
    return items;
  },
  // Venn Diagram
  venn: function () {
    return [{
      text: 'Groups',
      iconCls: '',
      menu: this.buildGroupMenu('vennGroups', [1, 2, 3, 4])
    }]
  },
  // Pie graphs
  pie: function () {
    return [{
      text: 'Style',
      iconCls: '',
      menu: this.buildGroupMenu('pieType', ['solid', 'separated'])
    }, {
      text: 'Precision',
      iconCls: '',
      menu: this.addFormParameter('pieSegmentPrecision')
    }, {
      text: 'Separation',
      iconCls: '',
      menu: this.addFormParameter('pieSegmentSeparation')
    }, {
      text: 'Labels',
      iconCls: '',
      menu: this.buildGroupMenu('pieSegmentLabels', ['inside', 'outside'])
    }];
  },
  // Networks
  networks: function() {
    return [{
      text: 'Animation',
      iconCls: '',
      menu: this.networkAnimation()
    }, {
      text: 'Pre-Scale',
      iconCls: '',
      menu: this.buildGroupMenu('preScaleNetwork', [true, false])
    }, {
      text: 'Nodes',
      iconCls: '',
      menu: this.networkNodes()
    }, {
      text: 'Random Networks',
      iconCls: '',
      menu: this.networkRandom()
    }];
  },
  networkAnimation: function () {
    return [{
      text: 'Show',
      iconCls: '',
      menu: this.buildGroupMenu('showAnimation', [true, false])
    }, {
      text: 'Font',
      iconCls: '',
      menu: this.networkAnimationFont()
    }];
  },
  networkAnimationFont: function () {
    return [{
      text: 'Size',
      iconCls: '',
      menu: this.addFormParameter('showAnimationFontSize')
    }, {
      text: 'Color',
      iconCls: '',
      menu: this.colorMenu('showAnimationFontColor')
    }];
  },
  networkNodes: function () {
    return [{
      text: 'Threshold Number',
      iconCls: '',
      menu: this.addFormParameter('showNodeNameThreshold')
    }, {
      text: 'Font',
      iconCls: '',
      menu: this.networkNodesFont()
    }];
  },
  networkNodesFont: function () {
    return [{
      text: 'Size',
      iconCls: '',
      menu: this.addFormParameter('nodeFontSize')
    }, {
      text: 'Color',
      iconCls: '',
      menu: this.colorMenu('nodeFontColor')
    }];
  },
  networkRandom: function () {
    return [{
      text: 'Generate',
      iconCls: '',
      menu: this.buildGroupMenu('randomNetwork', [true, false])
    }, {
      text: 'Node Number',
      iconCls: '',
      menu: this.addFormParameter('randomNetworkNodes')
    }, {
      text: 'Max Edges / Node',
      iconCls: '',
      menu: this.addFormParameter('randomNetworkNodeEdgesMax')
    }];
  },
  // Genome Browser
  genomeBrowser: function() {
    return [{
      text: 'Tracks',
      iconCls: '',
      menu: this.genomeBrowserTracks()
    }, {
      text: 'Features',
      iconCls: '',
      menu: this.genomeBrowserFeatures()
    }, {
      text: 'Sequence',
      iconCls: '',
      menu: this.genomeBrowserSequence()
    }, {
      text: 'Wire Color',
      iconCls: '',
      menu: this.colorMenu('wireColor')
    }, {
      text: 'Ticks',
      iconCls: '',
      menu: this.genomeBrowserTicks()
    }];
  },
  genomeBrowserTracks: function() {
    return [{
      text: 'Font',
      iconCls: '',
      menu: this.genomeBrowserTracksFont()
    }];
  },
  genomeBrowserTracksFont: function() {
    return [{
      text: 'Size',
      iconCls: '',
      menu: this.addFormParameter('trackNameFontSize')
    }, {
      text: 'Color',
      iconCls: '',
      menu: this.colorMenu('trackNameFontColor')
    }];
  },
  genomeBrowserFeatures: function() {
    return [{
      text: 'Threshold Number',
      iconCls: '',
      menu: this.addFormParameter('showFeatureNameThereshold')
    }, {
      text: 'Font',
      iconCls: '',
      menu: this.genomeBrowserFeaturesFont()
    }, {
      text: 'Defaults',
      iconCls: '',
      menu: this.genomeBrowserFeaturesDefaults()
    }];
  },
  genomeBrowserFeaturesFont: function() {
    return [{
      text: 'Size',
      iconCls: '',
      menu: this.addFormParameter('featureNameFontSize')
    }, {
      text: 'Color',
      iconCls: '',
      menu: this.colorMenu('featureNameFontColor')
    }];
  },
  genomeBrowserFeaturesDefaults: function() {
    return [{
      text: 'Width',
      iconCls: '',
      menu: this.addFormParameter('featureWidthDefault')
    }, {
      text: 'Height',
      iconCls: '',
      menu: this.addFormParameter('featureHeightDefault')
    }, {
      text: 'Type',
      iconCls: '',
      menu: this.addFormParameter('featureTypeDefault', true)
    }];
  },
  genomeBrowserSequence: function() {
    return [{
      text: 'Font Size',
      iconCls: '',
      menu: this.addFormParameter('sequenceFontSize')
    }, {
      text: 'A Color',
      iconCls: '',
      menu: this.colorMenu('sequenceAColor')
    }, {
      text: 'C Color',
      iconCls: '',
      menu: this.colorMenu('sequenceCColor')
    }, {
      text: 'G Color',
      iconCls: '',
      menu: this.colorMenu('sequenceGColor')
    }, {
      text: 'T Color',
      iconCls: '',
      menu: this.colorMenu('sequenceTColor')
    }, {
      text: 'Multiple Color',
      iconCls: '',
      menu: this.colorMenu('sequenceMColor')
    }];
  },
  genomeBrowserTicks: function() {
    return [{
      text: 'Number',
      iconCls: '',
      menu: this.addFormParameter('ticks')
    }, {
      text: 'Label Periodicity',
      iconCls: '',
      menu: this.addFormParameter('periodTicksLabels')
    }];
  },
  graphTypes: function () {
    if (this.canvas.layoutComb) {
      var items = [];
      var c = 0;
      for (var i = 0; i < this.canvas.layoutRows; i++) {
	for (var j = 0; j < this.canvas.layoutCols; j++) {
	  var lab = 'Graph ' + (c + 1);
	  items.push({
	    text: lab,
	    iconCls: '',
	    menu: this.buildGroupMenu('subGraphType' + c, this.canvas.getValidGraphTypes())
	  });
	  c++;
	}
      }
      return items;
    } else {
      return this.buildGroupMenu('graphType', this.canvas.getValidGraphTypes());
    }
  },
  endDrag: function(n) {
    if(n && n.nodes && n.nodes.length)
    {
      for(var i = 0; i < n.nodes.length; i++)
        this.addNode(n.nodes[i]);
      this.fireEvent('endnodedrag', n.nodes, function(s) {
        if(s)
          for(var i = 0; i < n.nodes.length; i++)
            this.removeNode(n.nodes[i].id);
      }.createDelegate(this));
    }
    if(n && n.legend)
      this.updateLegend();
  },
  toggleChildren: function(b, e, n) {
    if(b.text.match(/expand/i)) n.hideChildren = false;
    else n.hideChildren = true;
    this.addNode(n);
    this.fireEvent('expandgroup', n, this.removeNode.createDelegate(this, [n.id]));
    this.canvas.draw();
  },
  toggleNode: function(n, hide) {
    this.canvas.hideUnhideNodes([n.id], hide);
    this.addNode(n);
    this.fireEvent('togglenode', n, hide, this.removeNode.createDelegate(this, [n.id]));
    this.canvas.draw();
  },
  changeNodeOrder: function(n, dir) {
    this.canvas[dir](n);
    this.updateOrder();
    this.canvas.draw();
  },
  editNode: function(b, e, o) {
    var w = new Ext.canvasXpress.nodeDialog(o, this);
    w.show();
  },
  editEdge: function(b, e, o, dir) {
    var w = new Ext.canvasXpress.edgeDialog(o, dir, this);
    w.show();
  },
  editLegend: function(b, e, type, o) {
    var w = type == 'node'? new Ext.canvasXpress.nodeLegendDialog(o, this) :
            type == 'edge'? new Ext.canvasXpress.edgeLegendDialog(o, this) :
            new Ext.canvasXpress.textLegendDialog(o, this);
    w.show();
  },
  updateLegend: function() {
    this.legendChanged = true;
    this.fireEvent('updatelegend', function(s) {
        if(s) this.legendChanged = false;
      }.createDelegate(this));
  },
  updateOrder: function() {
    this.orderChanged = true;
    this.fireEvent('updateorder', function(s) {
        if(s) this.orderChanged = false;
      }.createDelegate(this));
  },
  deleteLegend: function(type, o) {
    if(type == 'node' || type == 'edge')
      this.canvas.data.legend[type + 's'] = [];
    else
    {
      var t = this.canvas.data.legend.text;
      for(var i = 0; i < t.length; i++)
        if(t[i] == o)
        {
          this.canvas.data.legend.text.splice(i, 1);
          break;
        }
    }
    this.updateLegend();
    this.canvas.draw();
  },
  deleteNode: function(n) {
    Ext.Msg.confirm('Warning', 'Are you sure you want to delete this node? This node and all of its edges and child nodes will be deleted!', function(b) {
      if(b == 'yes')
      {
        this.fireEvent('removenode', n, function() {
          this.canvas.removeNode(n);
          this.canvas.draw();
          this.updateOrder(); // change of # of node causes nodeIndices to change, it has to be consistent!!
        }.createDelegate(this));
      }
    }, this)
  },
  deleteEdge: function(e) {
    Ext.Msg.confirm('Warning', 'Are you sure you want to delete this edge?', function(b) {
      if(b == 'yes')
      {
        this.fireEvent('removeedge', e, function() {
          this.canvas.removeEdge(e);
          this.canvas.draw();
        }.createDelegate(this));
      }
    }, this)
  },
  editNetwork: function(b, e) {
    var config = {extCanvas:this};
    var d = new Ext.canvasXpress.networkDialog(this.canvas.data.info, this);
    d.show();
  },
  removeNode: function(id) {
    for(var i = 0; i < this.changedNodes.length; i++)
    {
      if(this.changedNodes[i].id == id)
        this.changedNodes.splice(i, 1);
    }
  },
  addNode: function(n) {
    for(var i = 0; i < this.changedNodes.length; i++)
      if(this.changedNodes[i].id == n.id)
        return;
    this.changedNodes.push(n);
  },
  removeEdge: function(id1, id2) {
    for(var i = 0; i < this.changedEdges.length; i++)
    {
      var e = this.changedEdges[i];
      if(e.id1 == id1 && e.id2 == id2)
        this.changedEdges.splice(i, 1);
    }
  },
  addEdge: function(ae) {
    for(var i = 0; i < this.changedEdges.length; i++)
    {
      var e = this.changedEdges[i];
      if(e.id1 == ae.id1 && e.id2 == ae.id2)
        return;
    }
    this.changedEdges.push(ae);
  },
  resetChanges: function() {
    this.changedNodes = [];
    this.changedEdges = [];
    this.legendChanged = false;
    this.orderChanged = false;
    this.networkChanged = false;
  },
  saveMap: function() {
    var d = this.canvas.data, obj = {nodes:this.changedNodes, edges:this.changedEdges};
    if(this.legendChanged) obj.legend = d.legend;
    if(this.orderChanged) obj.nodeIndices = d.nodeIndices;
    if(this.networkChanged) obj.info = d.info;
    // handler should redraw entire canvas if nodes and/or edges were added
    this.fireEvent('saveallchanges', obj, this.resetChanges.createDelegate(this));
  },
  storeSnapshot: function() {
    if(this.movieURL)
    {
      this.canvas.stopSnapshotPlay(true);
      var win = new Ext.Window({
        title: 'Store Current Snapshots to Database',
        width: 300,
        height: 200,
        layout: 'fit',
        items: {
          items: {
            xtype: 'form',
            border: false,
            defaultType: 'textfield',
            width: 280,
            labelWidth: 80,
            style:'margin:5px',
            items: [
              { fieldLabel: 'Name', value: this.snapshotsInfo? this.snapshotsInfo.name : '' },
              { fieldLabel: 'Description', value: (this.snapshotsInfo? this.snapshotsInfo.desc : ''), width: 170 },
              { xtype: 'checkbox', hideLabel: true, boxLabel: 'Shared with everyone?', checked: (this.snapshotsInfo? this.snapshotsInfo.shared : false) }
            ]
          }
        },
        bbar: {
          items: [
            '->',
            {
              text: 'Save to DB Now',
              scope: this,
              handler: function(b, e) {
                var f = b.ownerCt.ownerCt.get(0).get(0), name = f.get(0).getValue(),
                    desc = f.get(1).getValue(), shared = f.get(2).getValue();
                if(!name)
                {
                  Ext.Msg.alert('Error', 'Name must be filled out!');
                  return;
                }
                var id = (this.snapshotsInfo && this.snapshotsInfo.id)? this.snapshotsInfo.id : null;
                Ext.Ajax.request({
                  url: this.movieURL,
                  params: { action:'saveMovie', name: name, id: id,
                            pid:this.canvas.data.info.id,
                            data:Ext.encode(this.canvas.snapshots),
                            desc: desc, shared: shared? '1':'0' },
                  scope: this,
                  callback: function(o, s, r) {
                    if(!s) Ext.Msg.alert('Error', 'Could not save movie to server!');
                    else
                    {
                      var res = Ext.decode(r.responseText);
                      this.snapshotsInfo.id = res.id;
                      win.close();
                    }
                  }
                });
                this.snapshotsInfo = {name:name, desc:desc, shared:shared};
              }
            }
          ]
        }
      });
      win.show();
    }
  },
  toggleSnapshotCtrl: function(b, e) {
    if(!this.snapshotCtrl)
    {
      var items = [
        {
          icon: this.imgDir + 'eye.png',
          itemId: 'snap',
          tooltip: 'Take A Snapshot'
        },
        {
          itemId: 'play',
          menu: [
            {
              text: 'Every 50ms',
              handler: this.playSnapshot.createDelegate(this, [50], true)
            },
            {
              text: 'Every 200ms',
              handler: this.playSnapshot.createDelegate(this, [200], true)
            },
            {
              text: 'Every 500ms',
              handler: this.playSnapshot.createDelegate(this, [500], true)
            },
            {
              text: 'Every 1s',
              handler: this.playSnapshot.createDelegate(this, [1000], true)
            },
            {
              text: 'Every 2s',
              handler: this.playSnapshot.createDelegate(this, [2000], true)
            },
            {
              text: 'Every 5s',
              handler: this.playSnapshot.createDelegate(this, [5000], true)
            }
          ]
        },
        {
          icon: this.imgDir + 'stop.png',
          itemId: 'stop',
          tooltip: 'Stop Playing Snapshots'
        },
        {
          icon: this.imgDir + 'rewind.png',
          itemId: 'prev',
          tooltip: 'Previous Snapshot'
        },
        {
          icon: this.imgDir + 'fast_forward.png',
          itemId: 'next',
          tooltip: 'Next Snapshot'
        },
        {
          icon: this.imgDir + 'copy.png',
          itemId: 'copy',
          tooltip: 'Duplicate Current Snapshot'
        },
        {
          icon: this.imgDir + 'arrow_left.png',
          itemId: 'left',
          tooltip: 'Shift This Snapshot Left'
        },
        {
          icon: this.imgDir + 'arrow_right.png',
          itemId: 'right',
          tooltip: 'Shift This Snapshot Right'
        },
        {
          icon: this.imgDir + 'delete.png',
          itemId: 'delete',
          tooltip: 'Delete Current Snapshots'
        }
      ];
      if(this.movieURL)
        items.push(
          {
            icon: this.imgDir + 'turn_left.png',
            tooltip: 'Load Snapshots from DB',
            itemId: 'load'
          },
          {
            icon: this.imgDir + 'save.png',
            tooltip: 'Store Snapshots to DB',
            itemId: 'store'
          });
      items.push({
        icon: this.imgDir + 'help.png',
        itemId: 'help',
        handler: null
      }, {
        icon: this.imgDir + 'power_off.png',
        itemId: 'hide',
        tooltip: 'Hide This Toolbar (Shift-Click toggles this toolbar)',
        handler: this.toggleSnapshotCtrl
      });
      var xy = e.xy? e.xy : e;
      this.snapshotCtrl = new Ext.Window({
        height: 16,
        width: 270 + (this.movieURL? 42 : 0),
        x: xy[0],
        y: xy[1],
        border: false,
        closable: false,
        resizable: false,
        bbar: new Ext.Toolbar({
          defaults: {
            xtype: 'button',
            scope: this,
            handler: this.playSnapshot
          },
          items: items
        })
      });
    }
    if(this.snapshotCtrl.isVisible()) this.snapshotCtrl.hide();
    else this.snapshotCtrl.show(null, this.setCtrlMode, this);
  },
  enableCtrlButton: function(name, enabled) {
    var button = this.snapshotCtrl.getBottomToolbar().getComponent(name);
    if(button) button.setDisabled(!enabled);
  },
  changePlayIcon: function(name) {
    var button = this.snapshotCtrl.getBottomToolbar().getComponent('play');
    if(name == 'play')
    {
      button.setIcon(this.imgDir + 'play.png');
      button.setTooltip('Play Current Snapshots');
      button.setHandler(null);
    }
    else
    {
      button.setIcon(this.imgDir + 'pause.png');
      button.setTooltip('Pause Snapshot Play');
      button.setHandler(this.playSnapshot.createDelegate(this));
    }
  },
  setCtrlMode: function(mode) {
    this.enableCtrlButton('next', this.canvas.hasNextSnapshot());
    this.enableCtrlButton('prev', this.canvas.hasPrevSnapshot());
    this.enableCtrlButton('left', this.canvas.snapshotPaused && this.canvas.hasPrevSnapshot());
    this.enableCtrlButton('right', this.canvas.hasNextSnapshot());
    this.enableCtrlButton('copy', this.canvas.snapshots && this.canvas.snapshots.length);
    this.changePlayIcon((this.canvas.snapshotPaused || !this.canvas.snapshotPlay)? 'play' : 'pause');
    this.enableCtrlButton('play', this.canvas.snapshots && this.canvas.snapshots.length > 1);
    this.enableCtrlButton('stop', this.canvas.snapshotPlay);
    this.enableCtrlButton('store', this.canvas.snapshots && this.canvas.snapshots.length > 1);
    this.enableCtrlButton('delete', this.canvas.snapshots && this.canvas.snapshots.length);
    this.enableCtrlButton('snap', !this.canvas.snapshotPlay && !this.canvas.snapshotPaused);
    var button = this.snapshotCtrl.getBottomToolbar().getComponent('help');
    if(this.canvas.snapshotPlay)
    {
      if(this.canvas.snapshotPaused)
        button.setTooltip('Playing paused on snapshot #' + this.canvas.snapshotPlay.idx);
      else
        button.setTooltip('Currently playing snapshots at ' + this.canvas.snapshotPlay.time + ' ms/snapshot');
    }
    else if(this.canvas.snapshots && this.canvas.snapshots.length > 1)
      button.setTooltip('Has '+this.canvas.snapshots.length+' snapshots. Press the play button to view animation.');
    else if(this.canvas.snapshots && this.canvas.snapshots.length)
      button.setTooltip('Has only one snapshot, one more needed for animation.');
    else
      button.setTooltip('Has no snapshot yet. Animation requires at least 2 snapshots.');
  },
  playSnapshot : function(b, e, time) {
    if(b.text && b.text.match(/Every/))
      this.canvas.playSnapshot(time);
    else
    {
      switch (b.itemId)
      {
        case 'stop': this.canvas.stopSnapshotPlay(true); break;
        case 'play':
          if(this.canvas.snapshotPlay) // paused
          {
            if(b.hasVisibleMenu()) b.hideMenu();
            this.canvas.pauseSnapshot();
          }
          break;
        case 'delete':
          this.canvas.clearSnapshot();
          delete this.snapshotsInfo;
          break;
        case 'snap': this.canvas.saveSnapshot(); break;
        case 'next': this.canvas.nextSnapshotOnce(); break;
        case 'prev': this.canvas.prevSnapshotOnce(); break;
        case 'load': this.loadSnapshotList(); break;
        case 'store': this.storeSnapshot(); break;
        case 'copy': this.canvas.duplicateSnapshot(); break;
        case 'left': this.canvas.moveSnapshot(-1); break;
        case 'right': this.canvas.moveSnapshot(1); break;
      }
    }
    this.setCtrlMode();
  },
  loadSnapshotList: function() {
    if(!this.movieURL) return;
    this.showMask();
    Ext.Ajax.request({
        url: this.movieURL,
        params: { action:'listMovie', id:this.canvas.data.info.id },
        scope: this,
        callback: function(o, s, r) {
          this.hideMask();
          if(!s) Ext.Msg.alert('Error', 'Could not load snapshot list server!');
          else
          {
            var list = Ext.decode(r.responseText);
            // array of username, name, description, movieid, shared
            var win = new Ext.Window({
              title: 'List of Available Snapshots',
              width: 500,
              height: 300,
              layout: 'fit',
              items: {
                xtype: 'grid',
                border: false,
                autoExpandColumn: 'ssdesc',
                store: new Ext.data.ArrayStore({
                    autoDestroy: true,
                    data: list,
                    fields: [ 'username', 'name', 'desc', 'id', 'shared' ]
                  }),
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                cm: new Ext.grid.ColumnModel({
                    defaults: { sortable: true, width: 60 },
                    columns: [
                      { header: "User", dataIndex:'username' },
                      { header: "Name", dataIndex:'name', width: 90 },
                      { header: "Shared", dataIndex:'shared' },
                      { header: "Description", dataIndex:'desc', id: 'ssdesc' }
                  ]})
              },
              bbar: {
                items: [
                  '->',
                  {
                    text: 'Delete Selected Snapshots',
                    scope: this,
                    handler: function(b, e) {
                      Ext.Msg.confirm('Warning', 'Are you sure you want to delete this movie?', function(t) {
                        if(t == 'yes')
                        {
                          var g = b.ownerCt.ownerCt.get(0), r = g.getSelectionModel().getSelected();
                          if(r && r.data)
                          {
                            this.showMask('Deleting snapshots ...');
                            Ext.Ajax.request({
                              url: this.movieURL,
                              params: { action:'deleteMovie', id: r.data.id },
                              scope: this,
                              callback: function(o, s, re) {
                                this.hideMask();
                                var res = (s && re && re.responseText)? Ext.decode(re.responseText) : null;
                                if(!res || res.error) Ext.Msg.alert('Error', res && res.error? res.error : 'Could not delete snapshots from server!');
                                else
                                {
                                  g.store.remove(r);
                                  Ext.Msg.alert('Done!', 'Snapshots deleted from the server!');
                                }
                              }
                            });
                          }
                        }
                      }, this);
                    }
                  },
                  {
                    text: 'Load Selected Snapshots',
                    scope: this,
                    handler: function(b, e) {
                      var g = b.ownerCt.ownerCt.get(0), r = g.getSelectionModel().getSelected();
                      if(r && r.data && this.movieURL)
                      {
                        this.showMask('Loading snapshots ...');
                        this.snapshotsInfo = r.data;
                        Ext.Ajax.request({
                          url: this.movieURL,
                          params: { action:'loadMovie', id: r.data.id },
                          scope: this,
                          callback: function(o, s, r) {
                            this.hideMask();
                            if(!s) Ext.Msg.alert('Error', 'Could not load movie from server!');
                            else
                            {
                              var res = Ext.decode(r.responseText);
                              this.canvas.snapshots = Ext.decode(res.data);
                              win.close();
                              this.setCtrlMode();
                            }
                          }
                        });
                      }
                    }
                  }
                ]
              }
            });
            win.show();
          }
        }
      });
  },
  showMask: function(msg) // pass in msg to override default msg
  {
    var defaultMsg = 'Loading ...';
    if(!this.mask) this.mask = new Ext.LoadMask(this.id, {msg:msg || defaultMsg});
    else if(!msg) this.mask.msg = defaultMsg;
    else if(msg) this.mask.msg = msg;
    this.mask.show();
  },
  hideMask: function()
  {
    if(this.mask) this.mask.hide();
  }
});
Ext.canvasXpress.utils = {
  removeNode: function(all, id) {
    for(var i = 0; i < this.changedNodes.length; i++)
    {
      if(this.changedNodes[i].id == n.id)
        this.changedNodes[i].splice(i, 1);
    }
  },
  customPanel: function(ps, ed) {
    // it's nicer to remove the item instead of hiding them (due to sending data AND the looks due to margin)
    for(var i = 0; i < ps.length; i++)
    {
      var a = ps[i].items;
      for(var j = a.length - 1; j >= 0; j--)
        if(a[j].hidden) a.splice(j, 1);
    }
    if(ed.panels)
    {
      for(var i = 0; i < ed.panels.length; i++)
        ps.push(ed.panels[i]);
    }
    if(ed.addToPanels)
    {
      for(var i = 0; i < ed.addToPanels.length; i++)
      {
        var o = ed.addToPanels[i];
        ps[o.pidx || 0].items.push(o);
      }
    }
  },
  renderPanels: function(tab) { // make sure all tabs are rendered
    var active = tab.getActiveTab();
    for(var i = 0; i < tab.items.getCount(); i++)
    {
      var p = tab.get(i);
      if(!p.rendered) // we need to render it otherwise af.getValues() will break
        tab.activate(p); // render() should not and does not work
    }
    tab.activate(active);
  },
  resetForms: function(tab) {
    for(var i = 0; i < tab.items.getCount(); i++)
    {
      var p = tab.get(i);
      if(p.isXType('form'))
        p.getForm().reset();
    }
  },
  callback: function(cb, args) {
    if(cb.fn) cb.fn.apply(cb.scope || this, args);
    else cb.apply(this, args);
  },
  addMenu: function(items, o, f, scope) {
    if(f)
    {
      var mi = f.call(scope, o);
      if(mi)
        for(var i = 0; i < mi.length; i++)
          items.push(mi[i]);
    }
  },
  gridToLegend: function(extCanvas, grid, type) {
    extCanvas.canvas.data.legend[type] = [];
    var t = grid.getStore().data.items, l = extCanvas.canvas.data.legend[type];
    for(var i = 0; i < t.length; i++)
      l.push(t[i].data);
  },
  initLegend: function(type) {
    var xy = this.extCanvas.canvas.adjustedCoordinates(this.extCanvas.clickXY);
    if(!this.extCanvas.canvas.data.legend)
      this.extCanvas.canvas.data.legend = {nodes:[],edges:[]};
    if(!this.extCanvas.canvas.data.legend[type])
      this.extCanvas.canvas.data.legend[type] = [];
    if(!this.extCanvas.canvas.data.legend.pos)
      this.extCanvas.canvas.data.legend.pos = {type:xy};
    else if(!this.extCanvas.canvas.data.legend.pos[type] || this.extCanvas.canvas.data.legend.pos[type].x === false)
      this.extCanvas.canvas.data.legend.pos[type] = xy;
  },
  updateLegend: function(extCanvas, type) {
    if(!extCanvas.canvas.data.legend[type].length)
      extCanvas.canvas.data.legend.pos[type] = {x:false,y:false};
    extCanvas.updateLegend();
    extCanvas.canvas.draw();
  }
};
Ext.canvasXpress.nodeDialog = Ext.extend(Ext.Window, {
  title: 'Network Node Editor',
  constructor: function(config, extCanvas) {
    if(!config) config = {};
    this.nodeInfo = config;
    this.extCanvas = extCanvas;
    var allNodes = [], data = config.data || {}, parent = null, idMap = {}, clabel = config.label || config.name || config.id;
    for(var i in extCanvas.canvas.nodes)
    {
      var l = extCanvas.canvas.nodes[i], n = l.data, id = l.label || l.name || l.id;
      if(clabel != id)
      {
        allNodes.push(id);
        idMap[id] = l.id;
      }
      if(config.parentNode == i)
        parent = id;
    }
    allNodes.sort();
    var h = {}, nd = this.extCanvas.nodeDialog? this.extCanvas.nodeDialog(config) : {};
    this.nd = nd;
    if(nd.hide)
      for(var i = 0; i < nd.hide.length; i++)
        h[nd.hide[i]] = 1;
    var ps = [{
      title: 'Properties',
      items: [
        // label is required, parent, name, color, size, shape can all be hidden if user wants
        {
          xtype: 'compositefield',
          fieldLabel: 'Label',
          items: [
            { xtype: 'textfield', value: clabel || '',
              allowBlank: false, name:'label', width: 80 },
            { xtype: 'displayfield', value: 'Size:', width: 24, style:'margin-top:3px' },
            { xtype: 'numberfield', value: config.labelSize || 1,
              allowBlank: false, name:'labelSize', width: 30 },
            {
              xtype: 'checkbox',
              checked: config.hideName,
              boxLabel: 'Hide label?',
              name: 'hideName',
              flex: 1
            }
          ]
        },
        { fieldLabel: 'Name', value: config.name || '',
          hideLabel: h.name, hidden: h.name,
          allowBlank: false, name:'name' },
        {
          xtype: 'combo',
          fieldLabel: 'Parent',
          hideLabel: h.parent, hidden: h.parent,
          emptyText: 'Selection NOT Required',
          triggerAction: 'all',
          store: allNodes,
          value: parent,
          name: 'parentLabel'
        },
        { xtype: 'colorfield', fieldLabel: 'Color', allowBlank: false,
          name:'color', value: config.color || 'rgb(255,0,0)',
          hideLabel: h.color, hidden: h.color },
        { xtype:'numberfield', fieldLabel: 'Size', name:'size',
          hideLabel: h.size, hidden: h.size,
          value: config.size || '1.0', allowBlank:false },
        {
          xtype: 'combo',
          fieldLabel: 'Shape',
          allowBlank: false,
          hideLabel: h.shape, hidden: h.shape,
          emptyText: 'Selection Required',
          triggerAction: 'all',
          store: extCanvas.canvas.shapes.sort(),
          name: 'shape',
          value: config.shape || 'square'
        }
      ]
    }];
    Ext.canvasXpress.utils.customPanel(ps, nd);
    var bf = function(b, e, noClose) {
      var tab = b.ownerCt.ownerCt.get(0), prop = tab.get(0), pf = prop.getForm();
      Ext.canvasXpress.utils.renderPanels(tab);
      // validate data
      if(!pf.isValid()) tab.activate(prop);
      if(!pf.isValid() || (this.nd.isValid && !this.nd.isValid(tab)))
      {
        Ext.Msg.alert('Error', 'Required item not filled out or in wrong format!');
        return;
      }
      var p = pf.getValues();
      // enforce label unique policy (maybe not necessary and creates issue of adding same-labeled node after deletion due to a bug)
//       if(idMap[p.label] && prop.get(0).items.get(0).isDirty())
//       {
//         Ext.Msg.alert('Error', 'The label you entered conflict with another label in this network!\n\nPlease correct the problem and try again.');
//         return;
//       }
      // assembl parameters
      if(p.parentLabel && !p.parentLabel.match(/Selection/))
        p.parent = idMap[p.parentLabel];
      if(config.id) p.id = config.id;
      if(this.nd.getParams) this.nd.getParams.call(this, config, p, tab);
      var c = config.id? {x:config.x,y:config.y} : this.extCanvas.canvas.adjustedCoordinates(this.extCanvas.clickXY); // make sure there's an X,Y that user can save to DB in callback
      p.x = c.x; p.y = c.y;
      if(config.labelX)
      {
        p.labelX = config.labelX;
        p.labelY = config.labelY;
      }

      var f = function(n, p, res) {
        n.label = p.label;
        n.hideName = p.hideName;
        n.labelSize = p.labelSize;
        // if user sets them hidden, delegate these properties to user callbacks
        if(!h.name) n.name = p.name;
        if(!h.color) n.color = p.color;
        if(!h.size) n.size = p.size;
        if(!h.shape) n.shape = p.shape;
        if(p.parent) n.parentNode = p.parent;
        if(!n.id)
        {
          if(res && res.id) n.id = res.id;
          this.extCanvas.canvas.addNode(n, this.extCanvas.clickXY);
          this.extCanvas.updateOrder(); // change of # of node causes nodeIndices to change, it has to be consistent!!
        }
        this.extCanvas.canvas.draw();
        if(!res) // not saved to server
          this.extCanvas.addNode(n);
        else
          this.extCanvas.removeNode(n.id);
        if(!noClose) this.close();
      }.createDelegate(this);

      if(this.extCanvas.hasListener('updatenode'))
        this.extCanvas.fireEvent('updatenode', this.nodeInfo, p, f);
      else f(this.nodeInfo, p);
    }.createDelegate(this);
    var bitems = ['->'];
    if(config.id)
      bitems.push({
        text: 'Reset',
        scope: this,
        handler: function(b, e) { Ext.canvasXpress.utils.resetForms(b.ownerCt.ownerCt.get(0)) }
      },
      '|');
    bitems.push({
        text: 'Apply',
        handler: function(b, e) { bf(b, e, true) }
      },
      '|',
      {
        text: (config.id? 'Change' : 'Add') + ' Node',
        handler: bf
      });
    Ext.apply(this, {
      width: 350,
      height: 250,
      items: {
        xtype: 'tabpanel',
        activeItem: 0,
        defaultType: 'form',
        defaults: { style:'margin:5px',defaultType: 'textfield',height:210,labelWidth:80 },
        items: ps
      },
      bbar: bitems
    });
    Ext.canvasXpress.nodeDialog.superclass.constructor.apply(this);
  }
});
Ext.canvasXpress.edgeDialog = Ext.extend(Ext.Window, {
  title: 'Network Edge Editor',
  constructor: function(config, dir, extCanvas) {
    if(dir == 'to') config = {id2:config.id};
    else if(dir == 'from') config = {id1:config.id};
    else if(!config) config = {};
    this.edgeInfo = config;
    this.extCanvas = extCanvas;
    var allNodes = [], data = config.data || {}, idMap = {};
    for(var i in extCanvas.canvas.nodes)
    {
      var l = extCanvas.canvas.nodes[i], n = l.data, id = l.label || l.name || l.id;
      allNodes.push(id);
      idMap[id] = l.id;
    }
    allNodes.sort();
    var h = {}, ed = this.extCanvas.edgeDialog? this.extCanvas.edgeDialog(config) : {};
    this.ed = ed;
    if(ed.hide)
      for(var i = 0; i < ed.hide.length; i++)
        h[ed.hide[i]] = 1;
    var v1 = config.id1? extCanvas.canvas.nodes[config.id1] : null,
        v2 = config.id2? extCanvas.canvas.nodes[config.id2] : null;
    var ps = [{
      title: 'Customize',
      items: [
        {
          fieldLabel: 'Start Node',
          emptyText: 'Selection Required',
          triggerAction: 'all',
          store: allNodes,
          allowBlank: false,
          name: 'id1',
          value: v1? v1.label || v1.name || v1.id : null
        },
        {
          fieldLabel: 'End Node',
          emptyText: 'Selection Required',
          triggerAction: 'all',
          store: allNodes,
          allowBlank: false,
          name: 'id2',
          value: v2? v2.label || v2.name || v2.id : null
        },
        { name: 'width', xtype: 'numberfield', fieldLabel: 'Width',
          hideLabel: h.width, hidden: h.width,
          value: config.width || '2.0', allowBlank: false },
        {
          fieldLabel: 'Line Type',
          hideLabel: h.linetype, hidden: h.linetype,
          emptyText: 'Selection Required',
          triggerAction: 'all',
          store: extCanvas.canvas.lines,
          allowBlank: false,
          name: 'linetype',
          value: config.type || 'arrowHeadLine'
        },
        { xtype: 'colorfield', fieldLabel: 'Color', allowBlank: false,
          name:'color', value: config.color || 'rgb(255,0,0)',
          hideLabel: h.color, hidden: h.color }
      ]
    }];
    Ext.canvasXpress.utils.customPanel(ps, ed);
    var bbf = function(b, e, noClose) {
      var tab = b.ownerCt.ownerCt.get(0), fp = tab.get(0), bf = fp.getForm();
      Ext.canvasXpress.utils.renderPanels(tab);
      if(!bf.isValid() || (this.ed.isValid && !this.ed.isValid(tab)))
      {
        Ext.Msg.alert('Error', 'Required item not filled out or in wrong format!');
        return;
      }
      var p = bf.getValues();
      // assembl parameters
      p.entryid1 = idMap[p.id1];
      p.entryid2 = idMap[p.id2];
      if(this.ed.getParams) this.ed.getParams.call(this, config, p, tab);

      var f = function(e, p, res) {
        var add = !config.id1 || !config.id2;
        // if user sets them hidden, delegate these properties to user callbacks
        if(!h.width) e.width = p.width;
        if(!h.linetype) e.type = p.linetype;
        if(!h.color) e.color = p.color;
        e.id1 = p.entryid1;
        e.id2 = p.entryid2;
        if(add) this.extCanvas.canvas.addEdge(e);
        this.extCanvas.canvas.draw();
        if(!res) // not saved to server
          this.extCanvas.addEdge(e);
        else
          this.extCanvas.removeEdge(e.id1, e.id2);
        if(!noClose) this.close();
      }.createDelegate(this);

      if(this.extCanvas.hasListener('updateedge'))
        this.extCanvas.fireEvent('updateedge', this.edgeInfo, p, f);
      else f(this.edgeInfo, p);
    }.createDelegate(this);
    var bitems = ['->'];
    if(config.id)
      bitems.push({
        text: 'Reset',
        scope: this,
        handler: function(b, e) { Ext.canvasXpress.utils.resetForms(b.ownerCt.ownerCt.get(0)) }
      },
      '|');
    bitems.push({
        text: 'Apply',
        handler: function(b, e) { bbf(b, e, true) }
      },
      '|',
      {
        text: (config.id1 && config.id2? 'Change' : 'Add') + ' Edge',
        handler: bbf
      });
    Ext.apply(this, {
      width: 350,
      height: 250,
      items: {
        xtype: 'tabpanel',
        activeItem: 0,
        defaultType: 'form',
        defaults: { style:'margin:5px',defaultType: 'combo',height:210,labelWidth:80 },
        items: ps
      },
      bbar: bitems
    });
    Ext.canvasXpress.edgeDialog.superclass.constructor.apply(this);
  }
});
Ext.canvasXpress.networkDialog = Ext.extend(Ext.Window, {
  title: 'Network Editor',
  constructor: function(config, extCanvas) { // config should be the network obj (with (optional) id,name,(optional) description), with a (optional) key extCanvas being the panel
    if(!config) config = {};
    var ps = [{
      title: 'Customize',
      items: [
        {
          fieldLabel: 'Name',
          allowBlank: false,
          width: 170,
          name: 'name',
          value: config.name || ''
        },
        {
          fieldLabel: 'Description',
          width: 220,
          name: 'description',
          value: config.description || ''
        }
      ]
    }];
    var bitems = ['->'];
    if(config.id)
      bitems.push({
        text: 'Reset',
        scope: this,
        handler: function(b, e) { Ext.canvasXpress.utils.resetForms(b.ownerCt.ownerCt.get(0)) }
      },
      '|');
    bitems.push({
        text: (config.id? 'Change' : 'Add') + ' Network',
        scope: this,
        handler: function(b, e) {
          var tab = b.ownerCt.ownerCt.get(0), fp = tab.get(0), bf = fp.getForm();
          if(!bf.isValid())
          {
            Ext.Msg.alert('Error', 'Required item not filled out or in wrong format!');
            return;
          }
          this.networkChanged = true; // unfinished. add in user panel might be needed, combine with code in tree.js
          // add in delete this legend.
          var p = bf.getValues(), f = function() {
            this.networkChanged = false;
          };
          config.name = p.name;
          config.description = p.description;

          if(config.callback) config.callback(config, f);
          else if(extCanvas)
            extCanvas.fireEvent('updatenetwork', config, f);
          this.close();
        }
      });
    Ext.apply(this, {
      width: 350,
      height: 250,
      items: {
        xtype: 'tabpanel',
        activeItem: 0,
        defaultType: 'form',
        defaults: { style:'margin:5px',defaultType: 'textfield',height:210,labelWidth:80 },
        items: ps
      },
      bbar: bitems
    });
    Ext.canvasXpress.networkDialog.superclass.constructor.apply(this);
  }
});
Ext.canvasXpress.nodeLegendDialog = Ext.extend(Ext.Window, {
  title: 'Network NodeLegend Editor',
  constructor: function(config, extCanvas) {
    if(!config) config = {};
    this.confInfo = config;
    this.extCanvas = extCanvas;

    var cm = new Ext.grid.ColumnModel({
      defaults: { sortable: true },
      columns: [
        {
          header: 'Shape',
          dataIndex: 'shape',
          width: 70,
          editor: new Ext.form.ComboBox({ allowBlank: false,
              emptyText: 'Selection Required',
              triggerAction: 'all',
              store: extCanvas.canvas.shapes.sort() })
        },
        {
          header: 'Node Size',
          dataIndex: 'size',
          width: 70,
          editor: new Ext.form.NumberField({ allowBlank: false })
        },
        {
          header: 'Font Size',
          dataIndex: 'font',
          width: 70,
          editor: new Ext.form.NumberField({ allowBlank: false })
        },
        {
          header: 'Color',
          dataIndex: 'color',
          width: 150,
          editor: new Ext.ux.ColorField({ allowBlank: false })
        },
        {
          header: 'Text',
          dataIndex: 'text',
          editor: new Ext.form.TextField({ allowBlank: false })
        }
      ]
    });

    var store = new Ext.data.JsonStore({
      autoDestroy: true,
      root: 'nodes',
      fields: ['shape','text','color',{name:'size', type: 'float'},{name:'font', type: 'float'}]
    });
    Ext.canvasXpress.utils.initLegend.call(this, 'nodes');
    store.loadData(this.extCanvas.canvas.data.legend);

    // create the editor grid
    var width = 610, height = 300, grid;
    var ai = {
      text: 'Add Row',
      icon: this.extCanvas.imgDir + 'add.png',
      scope: this,
      handler: function(){
        var Node = grid.getStore().recordType;
        var n = new Node({
          color: 'rgb(255,0,0)',
          shape: 'square',
          font: 1,
          size: 1
        });
        grid.stopEditing();
        store.insert(0, n);
        grid.startEditing(0, 0);
        Ext.canvasXpress.utils.gridToLegend(extCanvas, grid, 'nodes');
      }
    }, ri = {
      text: 'Update Network',
      icon: this.extCanvas.imgDir + 'refresh.png',
      scope: this,
      handler: function(){
        Ext.canvasXpress.utils.gridToLegend(extCanvas, grid, 'nodes');
        Ext.canvasXpress.utils.updateLegend(extCanvas, 'nodes');
      }
    }, di = {
      text: 'Delete Selected Row',
      icon: this.extCanvas.imgDir + 'delete.png',
      scope: this,
      handler: function(){
        var c = grid.getSelectionModel().getSelectedCell();
        if(c)
        {
          grid.stopEditing();
          grid.getStore().removeAt(c[0]);
          Ext.canvasXpress.utils.gridToLegend(extCanvas, grid, 'nodes');
        }
      }
    };
    grid = new Ext.grid.EditorGridPanel({
      store: store,
      cm: cm,
      width: width - 10,
      height: height - 10,
      autoExpandColumn: 4, // 5th column, 'text'
      frame: false,
      clicksToEdit: 1,
      listeners: {
        scope: this,
        containercontextmenu: function(g, e) {
          e.stopEvent(); // here it's required, in TreePanel it's not.
          var m = new Ext.menu.Menu({ items: [ai, ri] });
          m.showAt(e.getXY());
        },
        contextmenu: function(e) {
          var c = grid.getSelectionModel().getSelectedCell();
          if(c)
          {
            e.stopEvent();
            var m = new Ext.menu.Menu({ items: di });
            m.showAt(e.getXY());
          }
        }
      },
      tbar: [ ai, di, ri ]
    });
    Ext.apply(this, {
      width: width,
      layout: 'fit',
      height: height,
      items: grid
    });
    Ext.canvasXpress.nodeLegendDialog.superclass.constructor.apply(this);
  }
});
Ext.canvasXpress.edgeLegendDialog = Ext.extend(Ext.Window, {
  title: 'Network EdgeLegend Editor',
  constructor: function(config, extCanvas) {
    if(!config) config = {};
    this.confInfo = config;
    this.extCanvas = extCanvas;

    var cm = new Ext.grid.ColumnModel({
      defaults: { sortable: true },
      columns: [
        {
          header: 'Line Type',
          dataIndex: 'type',
          width: 140,
          editor: new Ext.form.ComboBox({ allowBlank: false,
              emptyText: 'Selection Required',
              triggerAction: 'all',
              store: extCanvas.canvas.lines.sort() })
        },
        {
          header: 'Line Width',
          dataIndex: 'width',
          width: 70,
          editor: new Ext.form.NumberField({ allowBlank: false })
        },
        {
          header: 'Line Length',
          dataIndex: 'size',
          width: 70,
          editor: new Ext.form.NumberField({ allowBlank: false })
        },
        {
          header: 'Font Size',
          dataIndex: 'font',
          width: 70,
          editor: new Ext.form.NumberField({ allowBlank: false })
        },
        {
          header: 'Color',
          dataIndex: 'color',
          width: 150,
          editor: new Ext.ux.ColorField({ allowBlank: false })
        },
        {
          header: 'Text',
          dataIndex: 'text',
          editor: new Ext.form.TextField({ allowBlank: false })
        }
      ]
    });

    var store = new Ext.data.JsonStore({
      autoDestroy: true,
      root: 'edges',
      fields: ['type','text','color',{name:'size', type: 'float'},{name:'font', type: 'float'},{name:'width', type: 'float'}]
    });
    Ext.canvasXpress.utils.initLegend.call(this, 'edges');
    store.loadData(this.extCanvas.canvas.data.legend);

    // create the editor grid
    var width = 710, height = 300, grid;
    var ai = {
      text: 'Add Row',
      icon: this.extCanvas.imgDir + 'add.png',
      scope: this,
      handler: function(){
        var Edge = grid.getStore().recordType;
        var n = new Edge({
          type: 'arrowHeadLine',
          color: 'rgb(255,0,0)',
          font: 1,
          width: 1.5,
          size: 2
        });
        grid.stopEditing();
        store.insert(0, n);
        grid.startEditing(0, 0);
        Ext.canvasXpress.utils.gridToLegend(extCanvas, grid, 'edges');
      }
    }, ri = {
      text: 'Update Network',
      icon: this.extCanvas.imgDir + 'refresh.png',
      scope: this,
      handler: function(){
        Ext.canvasXpress.utils.gridToLegend(extCanvas, grid, 'edges');
        Ext.canvasXpress.utils.updateLegend(extCanvas, 'edges');
      }
    }, di = {
      text: 'Delete Selected Row',
      icon: this.extCanvas.imgDir + 'delete.png',
      scope: this,
      handler: function(){
        var c = grid.getSelectionModel().getSelectedCell();
        if(c)
        {
          grid.stopEditing();
          grid.getStore().removeAt(c[0]);
          Ext.canvasXpress.utils.gridToLegend(extCanvas, grid, 'edges');
        }
      }
    };
    grid = new Ext.grid.EditorGridPanel({
      store: store,
      cm: cm,
      width: width - 10,
      height: height - 10,
      autoExpandColumn: 5, // 6th column, 'text'
      frame: false,
      clicksToEdit: 1,
      listeners: {
        scope: this,
        containercontextmenu: function(g, e) {
          e.stopEvent(); // here it's required, in TreePanel it's not.
          var m = new Ext.menu.Menu({ items: [ai, ri] });
          m.showAt(e.getXY());
        },
        contextmenu: function(e) {
          var c = grid.getSelectionModel().getSelectedCell();
          if(c)
          {
            e.stopEvent();
            var m = new Ext.menu.Menu({ items: di });
            m.showAt(e.getXY());
          }
        }
      },
      tbar: [ ai, di, ri ]
    });
    Ext.apply(this, {
      width: width,
      layout: 'fit',
      height: height,
      items: grid
    });
    Ext.canvasXpress.edgeLegendDialog.superclass.constructor.apply(this);
  }
});
Ext.canvasXpress.textLegendDialog = Ext.extend(Ext.Window, {
  title: 'Network TextLegend Editor',
  constructor: function(config, extCanvas) {
    if(!config) config = {};
    this.confInfo = config;
    this.extCanvas = extCanvas;

    var cm = new Ext.grid.ColumnModel({
      defaults: { sortable: true },
      columns: [
        {
          header: 'Has Border?',
          dataIndex: 'boxed',
          width: 70,
          editor: new Ext.form.Checkbox({ allowBlank: false })
        },
        {
          header: 'Font Size',
          dataIndex: 'font',
          width: 70,
          editor: new Ext.form.NumberField({ allowBlank: false })
        },
        {
          header: 'Margin',
          dataIndex: 'margin',
          width: 100,
//           editor: new Ext.form.TextField({ allowBlank: false})
          editor: new Ext.form.TextField({ allowBlank: false,
                  invalidText: 'Allowed format: 10 or 10 20 or 15 20 40 or 10 15 40 30 (like CSS margin)',
                  regex: /^[0-9]+$|^[0-9]+[,\s]+[0-9]+$|^[0-9]+[,\s]+[0-9]+[,\s]+[0-9]+$|^[0-9]+[,\s]+[0-9]+[,\s]+[0-9]+[,\s]+[0-9]+$/, })
        },
        {
          header: 'Color',
          dataIndex: 'color',
          width: 150,
          editor: new Ext.ux.ColorField({ allowBlank: false })
        },
        {
          header: 'Text',
          dataIndex: 'text',
          editor: new Ext.form.TextField({ allowBlank: false })
        }
      ]
    });

    var store = new Ext.data.JsonStore({
      autoDestroy: true,
      root: 'text',
//       fields: ['text','id','color',{name:'boxed', type: 'boolean'},{name:'margin', type: 'float'},{name:'font', type: 'float'},{name:'x', type: 'float'},{name:'y', type: 'float'}]
      fields: ['text','id','color','margin',{name:'boxed', type: 'boolean'},{name:'font', type: 'float'},{name:'x', type: 'float'},{name:'y', type: 'float'}]
    });
    Ext.canvasXpress.utils.initLegend.call(this, 'text');
    store.loadData(this.extCanvas.canvas.data.legend);

    // create the editor grid
    var width = 610, height = 300, grid;
    var ai = {
      text: 'Add Row',
      icon: this.extCanvas.imgDir + 'add.png',
      scope: this,
      handler: function(){
        var Text = grid.getStore().recordType;
        grid.stopEditing();
        store.insert(0, new Text({ font: 1, margin: 10, color: 'rgb(255,255,255)', boxed: true }));
        grid.startEditing(0, 0);
        Ext.canvasXpress.utils.gridToLegend(extCanvas, grid, 'text');
      }
    }, ri = {
      text: 'Update Network',
      icon: this.extCanvas.imgDir + 'refresh.png',
      scope: this,
      handler: function(){
        Ext.canvasXpress.utils.gridToLegend(extCanvas, grid, 'text');
        Ext.canvasXpress.utils.updateLegend(extCanvas, 'text');
      }
    }, di = {
      text: 'Delete Selected Row',
      icon: this.extCanvas.imgDir + 'delete.png',
      scope: this,
      handler: function(){
        var c = grid.getSelectionModel().getSelectedCell();
        if(c)
        {
          grid.stopEditing();
          grid.getStore().removeAt(c[0]);
          Ext.canvasXpress.utils.gridToLegend(extCanvas, grid, 'text');
        }
      }
    };
    grid = new Ext.grid.EditorGridPanel({
      store: store,
      cm: cm,
      width: width - 10,
      height: height - 10,
      autoExpandColumn: 4, // 5th column, 'text'
      frame: false,
      clicksToEdit: 1,
      listeners: {
        scope: this,
        viewready: function() {
          if(this.confInfo && this.confInfo.id)
          {
            var row = grid.getStore().find('id', this.confInfo.id);
            grid.view.focusRow(row);
            grid.getSelectionModel().select(row, 4); // select text column
          }
        },
        containercontextmenu: function(g, e) {
          e.stopEvent(); // here it's required, in TreePanel it's not.
          var m = new Ext.menu.Menu({ items: [ai, ri] });
          m.showAt(e.getXY());
        },
        contextmenu: function(e) {
          var c = grid.getSelectionModel().getSelectedCell();
          if(c)
          {
            e.stopEvent();
            var m = new Ext.menu.Menu({ items: di });
            m.showAt(e.getXY());
          }
        }
      },
      tbar: [ ai, di, ri ]
    });
    Ext.apply(this, {
      width: width,
      layout: 'fit',
      height: height,
      items: grid
    });
    Ext.canvasXpress.textLegendDialog.superclass.constructor.apply(this);
  }
});
Ext.reg('canvasxpress', Ext.canvasXpress);