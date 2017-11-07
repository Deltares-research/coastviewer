Vue.use(Vuetify);
new Vue({
  el: '#app',
  data: {
  },
  mounted: function(){
    mapboxgl.accessToken = 'pk.eyJ1Ijoic2lnZ3lmIiwiYSI6ImNqNmFzMTN5YjEyYzYzMXMyc2JtcTdpdDQifQ.Cxyyltmdyy1K_lvPY2MTrQ';
    var map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v9'
    });
  }
});
