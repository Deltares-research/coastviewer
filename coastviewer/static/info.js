Vue.component('page', {
  template: '#page'
});

new Vue({
  el: '#app',
  data: {
    clipped: false,
    drawer: true,
    fixed: false,
    items: [
      { icon: 'bubble_chart', title: 'Inspire' }
    ],
    miniVariant: false,
    right: true,
    rightDrawer: false,
    title: 'Vuetify.js'
  }
});
