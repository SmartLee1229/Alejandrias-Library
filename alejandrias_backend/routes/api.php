<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ApiUsuario\UsuarioController;
use App\Http\Controllers\ApiForo\ForoController;
use App\Http\Controllers\ApiCategoria\CategoriaController;
use App\Http\Controllers\ApiForo\PublicacionController;
use App\Http\Controllers\ApiForo\ComentarioController;


Route::post('/register', [UsuarioController::class, 'register']);
Route::post('/login', [UsuarioController::class, 'login']);
Route::get('/verificar-apodo/{apodo}', [UsuarioController::class, 'verificarApodo']);

Route::middleware('auth:sanctum')->group(function () {
    Route::post('/foros', [ForoController::class, 'store']);
    Route::put('/foros/{id}', [ForoController::class, 'update']);
    Route::delete('/foros/{id}', [ForoController::class, 'destroy']);
    Route::get('/mis-foros', [ForoController::class, 'misForos']);
});
Route::get('/foros-publicos', [ForoController::class, 'forosPublicos']);
Route::get('/foros', [ForoController::class, 'index']);
Route::get('/foros/{foro_id}', [ForoController::class, 'show']);

Route::get('/categorias', [CategoriaController::class, 'index']);
Route::get('/categorias/{categoria_id}', [CategoriaController::class, 'show']);
Route::post('/categorias', [CategoriaController::class, 'store']);
Route::get('/categorias/{categoria_id}/foros', [CategoriaController::class, 'foros']);

Route::get('/foros/{foroId}/publicaciones', [PublicacionController::class, 'index']);
Route::post('/foros/{foroId}/publicaciones', [PublicacionController::class, 'store']);
Route::get('/publicaciones/{id}', [PublicacionController::class, 'show']);
Route::put('/publicaciones/{id}', [PublicacionController::class, 'update']);
Route::delete('/publicaciones/{id}', [PublicacionController::class, 'destroy']);

Route::get('/publicaciones/{publicacionId}/comentarios', [ComentarioController::class, 'index']);
Route::post('/publicaciones/{publicacionId}/comentarios', [ComentarioController::class, 'store']);
Route::get('/comentarios/{id}', [ComentarioController::class, 'show']);
Route::put('/comentarios/{id}', [ComentarioController::class, 'update']);
Route::delete('/comentarios/{id}', [ComentarioController::class, 'destroy']);

Route::get('/recomendar', [ForoController::class, 'recomendar']);
