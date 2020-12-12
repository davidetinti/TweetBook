<template>
    <div id="map-section">
        <!-- Map -->
        <div id="map" class="d-flex"></div>
        <!--Buttons-->
        <b-button id="sibebar-button" v-b-toggle.sidebar-right>
            <em class="fas fa-align-justify"></em>
        </b-button>
        <div id="maps_button">
            <div id="heat_button" ref="heatmapb"></div>
            <div id="marker_button" ref="markerb"></div>
            <div id="img_button" ref="imgb"></div>
        </div>
        <!-- Geolocated sidebar -->
        <b-sidebar id="sidebar-right"
                   title="Geolocalizzati"
                   right
                   shadow
                   width="400px">
            <div class="geolocated-sidebar">
                <div class="maps-search-container d-flex flex-column">
                    <div class="maps-selection-bar d-flex justify-content-between align-items-center px-3">
                        <div style="color: rgb(22, 159, 242)">
                            <div v-if="page.selected_geo_tweets.length">
                                <strong>Selezionati (${page.selected_geo_tweets.length})</strong>
                            </div>
                        </div>
                        <div class="d-flex">
                            <div @click="selectAll()"
                                 style="color: rgb(22, 159, 242); cursor: pointer">
                                <strong>Seleziona tutti</strong>
                            </div>
                            <div class="px-2">•</div>
                            <div @click="deselectAll()"
                                 style="color: rgb(22, 159, 242); cursor: pointer">
                                <strong>Deseleziona tutti</strong>
                            </div>
                        </div>
                    </div>
                    <div class="maps-search-tweets-container p-2">
                        <div class="search-tweets-wrapper m-1"
                             v-for="(tweet, index) in geolocalized_tweet"
                             :key="index">
                            <div class="d-flex px-3 py-2 justify-content-between">
                                <div class="d-flex">
                                    <div class="picture-wrapper">
                                        <b-avatar class="mr-2"
                                                  :src="tweet.user.profile_image_url"></b-avatar>
                                    </div>
                                    <div class="content-wrapper d-flex flex-column">
                                        <div class="d-flex flex-wrap">
                                            <div class="mr-1">
                                                <strong>${tweet.user.name}</strong>
                                            </div>
                                            <div style="color: rgb(101, 119, 134)">
                                                @${tweet.user.screen_name}
                                            </div>
                                        </div>
                                        <div class="tweet-text">${tweet.text}</div>
                                    </div>
                                </div>
                                <div class="select-wrapper d-flex align-items-center pl-4">
                                    <div class="px-2 py-1 checkboxes"
                                         @click="toggleSelection(tweet, page.selected_geo_tweets)"
                                         style="border-radius: 7px; cursor: pointer"
                                         :style="{
                      backgroundColor:
                        page.selected_geo_tweets.indexOf(tweet) != -1
                          ? 'rgb(22, 159, 242)'
                          : 'rgb(101, 119, 134)',
                    }">
                                        <div style="width: 13px">
                                            ${page.selected_geo_tweets.indexOf(tweet) != -1 ? "✔" :
                                            "✘"}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </b-sidebar>
    </div>
</template>

<script>
    module.exports = {
        delimiters: ["${", "}"],
        data: function () {
            return {
                page_copy: null,
                layer: null,
                is_heatmap_shown: true,
                is_markermap_shown: true,
                is_imagemap_shown: true,
                layers: new google.maps.MVCObject(),
                map: null,
            };
        },
        props: {
            page: Object,
            to_insert: Array,
        },
        computed: {
            page_id: function () {
                return this.page ? this.page.id : null;
            },
            page_tweets: function () {
                return this.page ? this.page.tweets : null;
            },
            geolocalized_tweet: function () {
                let array = [];
                this.page.tweets.forEach((tweet) => {
                    if (tweet.place || tweet.places) array.push(tweet);
                });
                return array;
            },
        },
        methods: {
            /* Inizializza una mappa all'interno dell'elemento "element */
            initMap(element) {
                let center = {
                    lat: 44.456348,
                    lng: 11.574575,
                };

                this.map = new google.maps.Map(element, {
                    zoom: 4,
                    center: center,
                    mapTypeControl: false,

                    fullscreenControl: false,
                    streetViewControl: false,
                    mapTypeId: "satellite",
                });
                this.map.addListener("center_changed", () => {
                    this.page.maps.lat = this.map.center.lat();
                    this.page.maps.lng = this.map.center.lng();
                });
                this.map.addListener("zoom_changed", () => {
                    this.page.maps.zoom = this.map.zoom;
                });
                var heatMapDiv = this.$refs.heatmapb;
                var markerMapDiv = this.$refs.markerb;
                var imageMapDiv = this.$refs.imgb;
                var vue = this;
                this.centerControl(heatMapDiv, markerMapDiv, imageMapDiv);
            },
            centerControl(heatdiv, markerdiv, imagediv) {
                let vue = this;
                return new Promise(function (resolve, reject) {
                    var controlUI = document.createElement("button");
                    controlUI.setAttribute("type", "button");
                    controlUI.setAttribute("class", "map_layer btn btn-dark");
                    controlUI.innerHTML = "Concentrazione";
                    controlUI.title =
                        "Premi per visualizzare o nascondere la HeatMap di concentrazione.";
                    heatdiv.appendChild(controlUI);
                    controlUI.addEventListener("click", () => {
                        if (vue.layer != null) {
                            if (!vue.is_heatmap_shown) {
                                vue.is_heatmap_shown = true;
                                vue.reloadHeatMap();
                            } else {
                                vue.is_heatmap_shown = false;
                                vue.layer.setMap(null);
                            }
                        } else window.alert("Nessun elemento disponibile nella mappa.");
                    });
                    var controlUI2 = document.createElement("button");
                    controlUI2.setAttribute("type", "button");
                    controlUI2.setAttribute("class", "map_layer btn btn-dark");
                    controlUI2.innerHTML = "Marker";
                    controlUI2.title =
                        "Clicca per mostrare o nascondere i Punti di Interesse e le Immagini nella mappa";
                    markerdiv.appendChild(controlUI2);
                    controlUI2.addEventListener("click", () => {
                        if (vue.page.maps.poi.length > 0) {
                            if (!vue.is_markermap_shown) {
                                vue.is_markermap_shown = true;
                                for (el of vue.page.maps.poi) {
                                    if (el.image == false) el.marker.setVisible(true);
                                }
                            } else {
                                vue.is_markermap_shown = false;
                                for (el of vue.page.maps.poi) {
                                    if (el.image == false) el.marker.setVisible(false);
                                    el.infowindow.close();
                                }
                            }
                        } else window.alert("Nessun elemento disponibile nella mappa.");
                    });
                    var controlUI3 = document.createElement("button");
                    controlUI3.setAttribute("type", "button");
                    controlUI3.setAttribute("class", "btn btn-dark");
                    controlUI3.innerHTML = "Immagini";
                    controlUI3.title =
                        "Clicca per mostrare o nascondere le immagini dalla mappa";
                    imagediv.appendChild(controlUI3);
                    controlUI3.addEventListener("click", () => {
                        let found = false;
                        if (vue.page.maps.poi.length > 0) {
                            for (el of vue.page.maps.poi) {
                                if (el.image == true) found = true;
                            }
                        }
                        if (found == true) {
                            if (!vue.is_imagemap_shown) {
                                vue.is_imagemap_shown = true;
                                for (el of vue.page.maps.poi) {
                                    if (el.image == true) el.marker.setVisible(true);
                                }
                            } else {
                                vue.is_imagemap_shown = false;
                                for (el of vue.page.maps.poi) {
                                    if (el.image == true) el.marker.setVisible(false);
                                    el.infowindow.close();
                                }
                            }
                        } else window.alert("Nessuna immagine disponibile nella mappa.");
                    });
                    resolve(true);
                });
            },
            toggleSelection(object, array) {
                var vue = this;
                if (array.indexOf(object) != -1) {
                    array.splice(array.indexOf(object), 1);
                    this.creationMarkerMap(object, false).then(function (result) {
                        vue.removeMarkers(null, result);
                    });
                } else {
                    array.push(object);
                    this.creationMarkerMap(object, true);
                }
            },
            selectAll() {
                this.deselectAll();
                this.page.selected_geo_tweets = this.geolocalized_tweet.slice();
                this.page.selected_geo_tweets.forEach((tweet) => {
                    this.creationMarkerMap(tweet, true);
                });
            },
            deselectAll() {
                while (this.page.maps.poi.length > 0)
                    this.removeMarkers(null, this.page.maps.poi[0]);
                this.page.selected_geo_tweets = [];
            },
            /* Cerca in un array di oggetti il primo oggetto
                        che ha la proprietà "fieldname" pari a "value" */
            /*connectData(fieldname, value, array) {
                      return true; // TODO non funziona per streaming, devo sistemare (riccio)
                      for (let i = 0; i < array.length; i++) {
                        if (array[i][fieldname] == value) return array[i];
                      }
                    },
                    */
            /* Cambia la posizione puntata dalla mappa */
            setMapLocation(lat, lng, zoom) {
                if (this.map) {
                    this.map.setCenter({
                        lat: lat,
                        lng: lng,
                    });
                    this.map.setZoom(zoom);
                }
            },
            /*Calcolo coordinate*/
            getCoordinates(tweet) {
                let lat, long;
                if (tweet.place) {
                    lat =
                        tweet.place.bounding_box.coordinates[0][1][1] +
                        tweet.place.bounding_box.coordinates[0][0][1] +
                        tweet.place.bounding_box.coordinates[0][2][1] +
                        tweet.place.bounding_box.coordinates[0][3][1];
                    long =
                        tweet.place.bounding_box.coordinates[0][1][0] +
                        tweet.place.bounding_box.coordinates[0][0][0] +
                        tweet.place.bounding_box.coordinates[0][2][0] +
                        tweet.place.bounding_box.coordinates[0][3][0];
                    lat = lat / 4;
                    long = long / 4;
                } else if (tweet.places) {
                    lat =  (tweet.places[0].geo.bbox[1] + tweet.places[0].geo.bbox[3]) / 2;
                    long = (tweet.places[0].geo.bbox[0] + tweet.places[0].geo.bbox[2]) / 2;
                }
                return new google.maps.LatLng(lat, long);
            },
            /* Crea heatmap */
            creationHeatMap() {
                var page = this.page.maps;
                page.heat_markers.splice(0, page.heat_markers.length);
                for (let tweet of this.page.tweets) {
                    if (tweet.place != null || tweet.geo != null) {
                        page.heat_markers.push(this.getCoordinates(tweet));
                    }
                }
            },
            reloadHeatMap() {
                if (this.layer != null) this.layer.setMap(null);
                // Reload the map with the new heatmap PoI
                if (this.is_heatmap_shown == true) {
                    this.layer = new google.maps.visualization.HeatmapLayer({
                        data: this.page.maps.heat_markers,
                    });
                    this.layer.setMap(this.map);
                }
            },
            imgSize(url, is_image) {
                return new Promise(function (resolve, reject) {
                    var img = new Image();
                    var width, height;
                    img.onload = function () {
                        width = img.width;
                        height = img.height;
                        scaling = Math.sqrt((width * height) / (is_image ? 15000 : 2500));
                        resolve({ width, height, scaling });
                    };
                    img.onerror = () => reject();
                    img.src = url;
                });
            },
            creationMarkerMap(tweet, insert_into_array) {
                var vue = this;
                return new Promise(function (resolve, reject) {
                    let tweet_url = "window.open('https://twitter.com/" + tweet.user.screen_name + "/status/" + tweet.id_str + "')";
                    var newpoi = null;
                    var result = null;
                    let is_image =
                        typeof tweet.extended_entities !== "undefined" ? true : false;
                    let url = is_image
                        ? tweet.extended_entities.media[0].media_url
                        : "../static/images/gps.png";
                    //Calcolo la grandezza dinamica dell'immagine
                    vue.imgSize(url, is_image).then(function (size) {
                        //Creazione POI
                        //Marker
                        let newmarker = new google.maps.Marker({
                            position: vue.getCoordinates(tweet),
                            icon: {
                                url: url,
                                scaledSize: new google.maps.Size(
                                    size.width / size.scaling,
                                    size.height / size.scaling
                                ),
                            },
                        });
                        //infowindow
                        const contentInfoWindow =
                            '<div class="d-flex flex-column"  id="content">' +
                            "<div>" +
                            "<a class='pointer_link' onclick=" +  tweet_url + ">" +
                            "<strong>" +
                            tweet.user.name +
                            "</strong>" +
                            "</a>" +
                            "</div>" +
                            "<div>" +
                            tweet.text +
                            "</div>" +
                            "</div>";
                        let newinfowindow = new google.maps.InfoWindow({
                            content: contentInfoWindow,
                            maxWidth: 250,
                        });
                        newmarker.addListener("click", () => {
                            newinfowindow.open(vue.map, newmarker);
                        });
                        //POI
                        newpoi = {
                            marker: newmarker,
                            infowindow: newinfowindow,
                            image: is_image,
                        };
                        vue.page.maps.poi.push(newpoi);
                        if (insert_into_array == true) {
                            newpoi.marker.setMap(vue.map);
                            newpoi.marker.setVisible(
                                newpoi.image ? vue.is_imagemap_shown : vue.is_markermap_shown
                            );
                            result = vue.page.maps.poi[vue.page.maps.poi.length - 1];
                        } else {
                            if (vue.page.maps.poi.length > 0)
                                result = vue.page.maps.poi.pop();
                        }
                        resolve(result);
                    });
                });
            },
            reloadMarkers(page) {
                //Riscrivo i marker non eliminati nella mappa
                for (poi of page.maps.poi)
                    poi.marker.setMap(this.map);
            },
            removeMarkers(page, element) {
                //Primo caso: nascondo tutti i marker di quella pagina.
                if (page != null && element == null) {
                    for (let poi of page.maps.poi) {
                        poi.infowindow.close();
                        poi.marker.setMap(null);
                    }
                }
                //Secondo caso: rimuovo completamente un marker
                else if (page == null && element != null) {
                    let indice = -1;
                    for (let i = 0; i < this.page.maps.poi.length; i++) {
                        if (
                            element.infowindow.content ===
                            this.page.maps.poi[i].infowindow.content
                        )
                            indice = i;
                    }
                    if (indice != -1) {
                        this.page.maps.poi[indice].infowindow.close();
                        this.page.maps.poi[indice].marker.setMap(null);
                        this.page.maps.poi.splice(indice, 1);
                    }
                } else console.error("Remove error!");
            },
        },
        watch: {
            page(new_value) {
                this.page_copy = new_value;
            },
            // azioni eseguite quando viene cambiata pagine, e quindi cambia il page_id
            page_id(new_value) {
                if (new_value) {
                    this.is_heatmap_shown = true;
                    this.is_imagemap_shown = true;
                    this.is_markermap_shown = true;
                    this.setMapLocation(
                        this.page.maps.lat,
                        this.page.maps.lng,
                        this.page.maps.zoom
                    );
                    this.reloadHeatMap();
                    this.reloadMarkers(this.page);
                }
            },
            page_tweets(new_value) {
                if (new_value) {
                    this.creationHeatMap();
                    this.reloadHeatMap();
                }
            },
            to_insert(new_value) {
                let a = [];
                if (new_value.length) {
                    new_value.forEach((tweet) => {
                        this.creationMarkerMap(tweet, true);
                        a.push(tweet);
                    });
                    this.$emit("inserted", a);
                }
            },
        },
        mounted: function () {
            this.page_copy = this.page;
            this.initMap(document.getElementById("map"));
        },
    };
</script>

<style>
    #maps_button {
        position: absolute;
        background-position-y: top;
        left: 25px;
        top: 15px;
    }

    #heat_button {
        margin-bottom: 3px;
    }

    #img_button {
        margin-top: 3px;
    }

    .pointer_link {
        cursor: pointer;
        text-decoration: none;
        font-weight: bold;
        color: black;
    }

    a:hover {
        text-decoration: none;
        color: black;
    }

    .gm-control-active,
    .gm-style-mtc > button {
        background-color: #333333 !important;
        color: white !important;
    }

    #map-section {
        height: 100%;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .geolocated-sidebar {
        width: var(--geolocated-sidebar);
    }

    .content-wrapper {
        word-break: break-word;
    }

    #map {
        height: 100%;
        width: calc(100%);
        color: black;
    }

    #sibebar-button {
        position: absolute;
        background-position-y: top;
        right: 15px;
        top: 60px;
    }

    .maps-search-container {
        width: var(--geolocated-sidebar);
        box-sizing: border-box;
    }

    .maps-selection-bar {
        height: var(--searchbar-height);
        width: var(--geolocated-sidebar);
        border-bottom: rgb(56, 68, 77) 1px solid;
        box-sizing: border-box;
        font-size: 13px;
    }

    .maps-search-tweets-container {
        width: var(--geolocated-sidebar);
        overflow-y: auto;
    }

        .maps-search-tweets-container::-webkit-scrollbar {
            display: none;
        }

    .search-tweets-wrapper {
        transition: 0.2s;
        border: 1px solid rgb(47, 51, 54);
        box-sizing: border-box;
        border-radius: 16px;
        width: 100%;
        background-color: rgb(0, 0, 0);
        color: white;
    }

        .search-tweets-wrapper:hover {
            transition: 0.2s;
            background-color: rgba(18, 21, 23, 0.7);
        }
</style>
