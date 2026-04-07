<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class IAService
{
    protected $url = 'http://127.0.0.1:8000/api/ia/';

    public function recomendar($intereses, $foros)
    {
        $response = Http::timeout(10)->post($this->url, [
            'tipo' => 'recomendador',
            'data' => [
                'intereses' => $intereses,
                'foros' => $foros
            ]
        ]);

        if ($response->failed()) {
            return [
                'error' => 'Error al conectar con IA'
            ];
        }

        return $response->json();
    }
}