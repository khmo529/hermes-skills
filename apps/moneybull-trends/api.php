<?php
/**
 * Plugin Name: MoneyBull Trends API
 * Description: 실시간 금융 트렌드 REST API.
 * Version: 1.0.0
 */

if (!defined('ABSPATH')) {
    exit;
}

add_action('rest_api_init', function () {
    register_rest_route('moneybull/v1', '/trends', [
        'methods' => 'GET',
        'callback' => 'moneybull_trends_api',
        'permission_callback' => '__return_true',
        'cache_timeout' => 55,
    ]);
});

function moneybull_trends_api( WP_REST_Request $request ) {
    $json = get_transient('moneybull_trends_json');
    if (!$json) {
        $path = wp_upload_dir()['basedir'] . '/moneybull/trends.json';
        if (!is_readable($path)) {
            return new WP_REST_Response(['error' => 'trends_not_ready'], 503);
        }
        $json = file_get_contents($path);
        set_transient('moneybull_trends_json', $json, 55);
    }
    $data = json_decode($json, true);
    if (!$data || empty($data['trends'])) {
        return new WP_REST_Response(['error' => 'invalid_payload'], 500);
    }
    return new WP_REST_Response(moneybull_trends_enrich($data), 200);
}

function moneybull_trends_enrich( array $payload ): array {
    foreach ($payload['trends'] as &$item) {
        $q = rawurlencode($item['keyword']);
        $item['url'] = home_url("/?s={$q}");
        $item['share_text'] = sprintf(
            'MoneyBull 실시간 금융 트렌드 %d위: %s',
            (int) $item['rank'],
            $item['keyword']
        );
    }
    return $payload;
}

add_action('moneybull_trends_sync', function () {
    $path = wp_upload_dir()['basedir'] . '/moneybull/trends.json';
    if (!is_readable($path)) {
        return;
    }
    set_transient('moneybull_trends_json', file_get_contents($path), 55);
    clean_term_cache(0, 'post_tag');
});
