<?php

namespace App\Http\Controllers\ApiForo;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Foro;
use App\Models\Usuario;
use App\Services\IAService;

class ForoController extends Controller
{
    public function index() {
        $foros = Foro::with(['usuario', 'categoria'])->get();

        return response()->json($foros, 200);
    }

    public function misForos()
{
    $usuario = auth()->user();

    if (!$usuario) {
        return response()->json(['error' => 'No autenticado'], 401);
    }

    $foros = Foro::where('foro_creador_id', $usuario->usuario_id)
        ->with(['usuario', 'categoria'])
        ->get();

    return response()->json($foros, 200);
}

    public function forosPublicos()
    {
        $foros = Foro::where('foro_privado', false)
            ->orWhereNull('foro_privado') 
            ->with(['usuario', 'categoria'])
            ->get();

        return response()->json($foros, 200);
    }

    public function store(Request $request)
{
    try {

        $usuario = auth()->user();

        if (!$usuario) {
            return response()->json(['error' => 'No autenticado'], 401);
        }

        if ($usuario->usuario_rol !== 'lider') {
            return response()->json(['error' => 'No autorizado'], 403);
        }

        $request->validate([
            'foro_titulo' => 'required|string',
            'foro_descripcion' => 'required|string',
            'foro_categoria_id' => 'required|exists:categoria,categoria_id',
        ]);

        $foro = new Foro();
        $foro->foro_titulo = $request->foro_titulo;
        $foro->foro_descripcion = $request->foro_descripcion;
        $foro->foro_categoria_id = $request->foro_categoria_id;
        $foro->foro_creador_id = $usuario->usuario_id;

        $foro->save();

        return response()->json($foro, 201);

    } catch (\Exception $e) {
        return response()->json([
            'error' => 'Error interno',
            'detalle' => $e->getMessage()
        ], 500);
    }
}
    
    public function show($id) {
        $foro = Foro::with(['usuario', 'categoria'])->find($id);

        if (!$foro) {
            return response()->json(['message' => 'Foro no encontrado'], 404);
        }

        return response()->json($foro, 200);
    }

    
   public function update(Request $request, $id)
{
    try {

        $usuario = auth()->user();

        if (!$usuario) {
            return response()->json(['error' => 'No autenticado'], 401);
        }

        if ($usuario->usuario_rol !== 'lider') {
            return response()->json(['error' => 'No autorizado'], 403);
        }

        $foro = Foro::find($id);

        if (!$foro) {
            return response()->json(['error' => 'Foro no encontrado'], 404);
        }

        if ($foro->foro_creador_id != $usuario->usuario_id) {
            return response()->json(['error' => 'No puedes editar este foro'], 403);
        }

        $foro->update($request->only([
            'foro_titulo',
            'foro_descripcion',
            'foro_categoria_id'
        ]));

        return response()->json([
            'mensaje' => 'Foro actualizado',
            'foro' => $foro
        ]);

    } catch (\Exception $e) {
        return response()->json([
            'error' => 'Error interno',
            'detalle' => $e->getMessage()
        ], 500);
    }
}
    
    public function destroy($id)
{
    try {

        $usuario = auth()->user();

        if (!$usuario) {
            return response()->json(['error' => 'No autenticado'], 401);
        }

        if ($usuario->usuario_rol !== 'lider') {
            return response()->json(['error' => 'No autorizado'], 403);
        }

        $foro = Foro::find($id);

        if (!$foro) {
            return response()->json(['error' => 'Foro no encontrado'], 404);
        }

        if ($foro->foro_creador_id != $usuario->usuario_id) {
            return response()->json(['error' => 'No puedes eliminar este foro'], 403);
        }

        $foro->delete();

        return response()->json([
            'mensaje' => 'Foro eliminado correctamente'
        ]);

    } catch (\Exception $e) {
        return response()->json([
            'error' => 'Error interno',
            'detalle' => $e->getMessage()
        ], 500);
    }
}
    public function recomendar(IAService $ia)
    {
        $user = auth()->user();

        $intereses = $user->intereses ?? null;

        $foros = Foro::pluck('titulo');

        $resultado = $ia->recomendar($intereses, $foros);

        return response()->json($resultado);
    }
}
