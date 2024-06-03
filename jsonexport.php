<?php
/*
Plugin Name: OV JSON Export 
Description: Gibt alle Posts und Seiten als JSON aus und fügt eine Admin-Seite hinzu.
Version: 1.0
Author: Ovenga Media
*/

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

// Hauptfunktion zum Abrufen der Posts und Seiten als JSON
function json_export_get_posts_and_pages() {
    // Argumente für WP_Query
    $args = array(
        'post_type' => array('post', 'page'),
        'posts_per_page' => -1
    );

    // WP_Query ausführen
    $query = new WP_Query($args);

    // Array zum Speichern der Ergebnisse
    $results = array();

    // Schleife durch die Abfrageergebnisse
    if ($query->have_posts()) {
        while ($query->have_posts()) {
            $query->the_post();
            $content = get_the_content();
            // HTML-Kommentare entfernen
            $content = preg_replace('/<!--(.*?)-->/', '', $content);
            // HTML-Entities dekodieren
            $content = html_entity_decode($content, ENT_QUOTES | ENT_XML1, 'UTF-8');
            // HTML-Tags entfernen
            $content = wp_strip_all_tags($content);
            // Mehrfache Zeilenumbrüche durch einen ersetzen
            $content = preg_replace('/\n+/', "\n", $content);
            $results[] = array(
                'ID' => get_the_ID(),
                'title' => get_the_title(),
                'content' => $content,
                'permalink' => get_permalink()
            );
        }
    }

    // Post-Daten zurücksetzen
    wp_reset_postdata();

    // JSON-Antwort zurückgeben
     return new WP_REST_Response($results, 200, array('Content-Type' => 'application/json; charset=UTF-8'));
    // return json_encode($results, JSON_PRETTY_PRINT);
}

// REST-API-Route registrieren
function json_export_register_route() {
    register_rest_route('json-export/v1', '/posts-pages', array(
        'methods' => 'GET',
        'callback' => 'json_export_get_posts_and_pages'
    ));
}
add_action('rest_api_init', 'json_export_register_route');

// Admin-Menü hinzufügen
function json_export_add_admin_menu() {
    add_menu_page(
        'JSON Export', // Seitentitel
        'JSON Export', // Menü-Titel
        'manage_options', // Berechtigungen
        'json-export', // Menü-Slug
        'json_export_admin_page' // Funktion zur Ausgabe der Seite
    );
}
add_action('admin_menu', 'json_export_add_admin_menu');

// Admin-Seiteninhalt
function json_export_admin_page() {
    ?>
    <div class="wrap">
        <h1>JSON Export</h1>
        <p>Um alle Posts und Seiten als JSON zu exportieren, klicken Sie auf den folgenden Link:</p>
        <a href="<?php echo esc_url(home_url('/wp-json/json-export/v1/posts-pages')); ?>" target="_blank">
            JSON Export URL
        </a>
    </div>
    <?php
}
