Vue.component('info-page', {
  props:["id"],
  data () {
     return {
       graph: null
     }
  },
  mounted() {
    this.createGraph()
    this.updateGraph()
  },
  methods: {
    exportGraph(){
      let src = this.graph.getDataURL({
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      let download = document.createElement('a')
      download.href = src
      download.download = 'screenshot.png'
      download.click();
   },
    createGraph(){
      var dom = document.getElementById("echart-container")
      this.graph = echarts.init(dom)

    },
    updateGraph(){
      const transect_id = this.id
      fetch(`/coastviewer/1.1.0/transects/${transect_id}/plot/eeg`, {

      })
      .then(response => {
        const resp_json =  response.json()
        return resp_json
      }).then(resp_json => {



        function createJetColormap (nshades) {
            // from https://github.com/bpostlethwaite/colormap/blob/master/index.js
            // You could also invert this colormap
            // const jeti = [{"index":0,"rgb":[0,0,131]},{"index":0.125,"rgb":[0,60,170]},{"index":0.375,"rgb":[5,255,255]},{"index":0.625,"rgb":[255,255,0]},{"index":0.875,"rgb":[250,0,0]},{"index":1,"rgb":[128,0,0]}];
            const jet = [{"index":0,"rgb":[128,0,0]},{"index":0.125,"rgb":[250,0,0]},{"index":0.375,"rgb":[255,255,0]},{"index":0.625,"rgb":[5,255,255]},{"index":0.875,"rgb":[0,60,170]},{"index":1,"rgb":[0,0,131]}];

            var indicies, fromrgba, torgba,
                    nsteps, cmap, colormap,
                    nshades, colors, i;
            // map index points from 0..1 to 0..n-1
            indicies = jet.map(function(c) {
                return Math.round(c.index * nshades);
            });

            var steps = jet.map(function(c, i) {
                  var rgba = jet[i].rgb.slice();
                  return rgba
              });

            var colors = []
            for (i = 0; i < indicies.length-1; ++i) {
                    nsteps = indicies[i+1] - indicies[i];
                    fromrgba = steps[i];
                    torgba = steps[i+1];

                    for (var j = 0; j < nsteps; j++) {
                        var amt = j / nsteps
                        colors.push([
                            Math.round(lerp(fromrgba[0], torgba[0], amt)),
                            Math.round(lerp(fromrgba[1], torgba[1], amt)),
                            Math.round(lerp(fromrgba[2], torgba[2], amt))
                        ]) }
                }

            //add 1 step as last value
            colors.push(jet[jet.length - 1].rgb);
            colors = colors.map( rgb2hex );
            return colors;
        };
        function rgb2hex (rgba) {
            var dig, hex = '#';
            for (var i = 0; i < 3; ++i) {
                dig = rgba[i];
                dig = dig.toString(16);
                hex += ('00' + dig).substr( dig.length ); }
            return hex; }

        function lerp(v0, v1, t) { return v0*(1-t)+v1*t }



        const series_object = {type: 'line', smooth: true, seriesLayoutBy: 'row',
        markLine: {
          symbol: 'none',
          lineStyle: {
            color: '#000'
          },
          label: {
            position: 'start',
            // normal: {
            //   show: false
            //   //name:'RSP'
            // },
            // emphasis: {show: false}
          },
          data: [ { name: 'RSP Lijn',
                    xAxis: resp_json.data[0].slice(1).findIndex(rsp => rsp === 0)+1,
                    itemStyle: {
                          color: '#000'
                      },
                    label: {
            formatter: '{b}',
            position: 'insideEndTop'
          }} ] //around the 0 value on the x-Axis
          }
        }
        const series = []
        const selected = {}

        Object.keys(resp_json.data).forEach(row => {
          if (resp_json.data[row][0]!=='cross_shore') {
            series.push(series_object)
            selected[resp_json.data[row][0].toString()] = true
          }
        })

        //series.push({})
        let options = {
          //color: ["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"],
          color: createJetColormap (resp_json.data.length-1),
          legend: {
            padding: [0, 0, 0, 0],
            itemGap: 2,
            selector: [
              {
                type: 'all or inverse',
                // can be any title you like
                title: 'All'
            },
          ],

            selectorPosition: 'start',
            selectorItemGap: 0.5,
            selectorButtonGap: 2,
            selected: selected
          },
          tooltip: {
            trigger: 'axis'
          },
          dataset: {
            source: resp_json.data //data
          },
          xAxis: {type: 'category',
                  name: 'x [m]',
                  interval: 5,
                  nameTextStyle:{
                    fontWeight: "bold",
                    fontSize: 11
                },
          },
          yAxis: {gridIndex: 0,
                  name: 'z [m]',
                  nameLocation: "middle",
                  nameTextStyle:{
                    fontWeight: "bold",
                    fontSize: 11,
                    align: "right",
                    padding: [0,8,0,0]
                  }
          },
          // markLine: {
          //   data: [ { name: 'RSP', xAxis: 0 } ]
          // },
          series: series
        }

        this.graph.clear()
        this.graph.setOption(options)
        this.graph.dispatchAction({
          type: 'brush',
          command: 'clear',
          areas: [],
        });

      })
    }
  },
  template: '#info-page'

})
new Vue({
  el: '#app',
  data: {
    fixed: true,
    title: 'Transect info page'
  }
})
