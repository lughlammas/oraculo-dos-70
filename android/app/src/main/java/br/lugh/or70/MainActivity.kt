package br.lugh.or70

import android.app.Activity
import android.app.AlertDialog
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.text.InputType
import android.view.Gravity
import android.view.View
import android.widget.*
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import org.json.JSONObject
import java.io.File

/** UI fina sobre o núcleo Python. Toda regra (cálculo, trava, hash) vive no or70; aqui só exibição e persistência do JSON. */
object Core {
    fun py(ctx: Context): com.chaquo.python.PyObject {
        if (!Python.isStarted()) Python.start(AndroidPlatform(ctx))
        return Python.getInstance().getModule("or70_bridge")
    }
    fun call(ctx: Context, fn: String, vararg a: Any): JSONObject = JSONObject(py(ctx).callAttr(fn, *a).toString())
}

class MainActivity : Activity() {
    private val BG = Color.rgb(14, 15, 20); private val FG = Color.rgb(232, 230, 222); private val CYAN = Color.rgb(0, 214, 230)
    private val ERR = Color.rgb(255, 120, 110)
    // Metais A–D (cor + letra + rótulo textual: diferenciação além da cor)
    private val METAL = mapOf("A" to Color.rgb(212, 175, 55), "B" to Color.rgb(192, 192, 200), "C" to Color.rgb(184, 115, 51), "D" to Color.rgb(120, 120, 128))
    private val METAL_NAME = mapOf("A" to "ouro", "B" to "prata", "C" to "bronze", "D" to "ferro")
    private val stateFile by lazy { File(filesDir, "current_drawstate.json") }
    private var state: JSONObject? = null
    private lateinit var root: LinearLayout; private lateinit var mesa: LinearLayout
    private lateinit var status: TextView; private lateinit var hashView: TextView; private lateinit var calc: TextView
    private lateinit var corr: TextView; private lateinit var reading: TextView
    private lateinit var btnReveal: Button; private lateinit var btnDraw: Button; private lateinit var btnPhys: Button

    private fun tv(s: String, size: Float = 14f, mono: Boolean = false, serif: Boolean = false, color: Int = FG) = TextView(this).apply {
        text = s; textSize = size; setTextColor(color); setTextIsSelectable(true); setPadding(0, 8, 0, 8)
        typeface = if (mono) Typeface.MONOSPACE else if (serif) Typeface.create(Typeface.SERIF, Typeface.BOLD) else Typeface.DEFAULT
    }
    private fun btn(s: String, f: () -> Unit) = Button(this).apply { text = s; isAllCaps = false; setOnClickListener { f() } }

    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(32, 48, 32, 48); setBackgroundColor(BG) }
        root.addView(tv("Oráculo dos 70", 26f, serif = true))
        root.addView(tv("núcleo or70 0.1 (Python real via Chaquopy) · offline", 12f, mono = true, color = CYAN))
        val seed = EditText(this).apply { hint = "seed (inteiro)"; inputType = InputType.TYPE_CLASS_NUMBER; setTextColor(FG); setHintTextColor(Color.GRAY); typeface = Typeface.MONOSPACE; setText("70") }
        val pieces = EditText(this).apply { hint = "físico: 3/4,4/0,5/2,… (topo/base, em ordem)"; setTextColor(FG); setHintTextColor(Color.GRAY); typeface = Typeface.MONOSPACE }
        btnDraw = btn("Sortear (simulado)") { set(Core.call(this, "draw_seed", seed.text.toString().ifBlank { "0" }, 7)) }
        btnPhys = btn("Registrar tiragem física") { set(Core.call(this, "draw_physical", pieces.text.toString())) }
        btnReveal = btn("Revelar e travar") { state?.let { set(Core.call(this, "reveal", it.toString())) } }
        root.addView(seed); root.addView(btnDraw); root.addView(pieces); root.addView(btnPhys)
        status = tv("", 14f, mono = true, color = CYAN); root.addView(status)
        root.addView(tv("Mesa", 18f, serif = true))
        mesa = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        root.addView(HorizontalScrollView(this).apply { addView(mesa) })
        root.addView(tv("Cálculo (dados operacionais)", 18f, serif = true)); calc = tv("", 13f, mono = true); root.addView(calc)
        root.addView(tv("Correspondências e evidência lexical", 18f, serif = true)); corr = tv("", 13f, mono = true); root.addView(corr)
        root.addView(tv("Leitura sugerida (autoral, não altera dados)", 18f, serif = true)); reading = tv("", 13f); root.addView(reading)
        root.addView(btnReveal)
        root.addView(tv("SHA-256 (hash completo do reveal)", 18f, serif = true)); hashView = tv("—", 12f, mono = true, color = CYAN); root.addView(hashView)
        root.addView(btn("Copiar hash") { copy("hash", hashView.text.toString()) })
        root.addView(btn("Verificar (hash + reprodução)") { state?.let { val r = Core.call(this, "verify", it.toString()); msg("Verificação", r.toString(2)) } })
        root.addView(btn("Testar trava (tentar editar leitura)") { state?.let { val r = Core.call(this, "try_set_reading", it.toString(), "edição pós-reveal"); msg("Trava", if (r.getBoolean("ok")) "Editável (não revelado)." else r.getString("error")) } })
        root.addView(btn("Revisar (nova versão vinculada)") { reviseDialog() })
        root.addView(btn("Exportar JSON (compartilhar + área de transferência)") { export() })
        root.addView(btn("Importar JSON da área de transferência") { import() })
        root.addView(btn("Ficha de auditoria") { state?.let { msg("Ficha", Core.call(this, "report", it.toString()).optString("text")) } })
        root.addView(btn("Nova consulta (descarta a atual da tela)") { state = null; stateFile.delete(); render() })
        setContentView(ScrollView(this).apply { setBackgroundColor(BG); addView(root) })
        if (stateFile.exists()) state = JSONObject(stateFile.readText(Charsets.UTF_8))  // persistência: trava vem do próprio JSON
        render()
    }

    private fun set(r: JSONObject) {
        if (!r.getBoolean("ok")) { msg("Rejeitado pelo núcleo", r.getString("error")); return }
        state = r.getJSONObject("state"); stateFile.writeText(state.toString(), Charsets.UTF_8); render()
    }

    private fun render() {
        mesa.removeAllViews(); val s = state
        if (s == null) { status.text = "sem consulta"; calc.text = ""; corr.text = ""; reading.text = ""; hashView.text = "—"; btnReveal.isEnabled = false; return }
        val d = s.getJSONObject("data"); val locked = s.getJSONObject("audit").getBoolean("locked"); val v = d.getJSONObject("validation")
        val ver = Core.call(this, "verify", s.toString())
        status.text = (if (locked) "■ TRAVADO v${s.getInt("version")} — hash_ok=${ver.opt("hash_ok")}" else "□ ABERTO v${s.getInt("version")} (não revelado)") +
            "\nvalidação: " + (if (v.getBoolean("valid")) "OK" else "ERRO ${v.getJSONArray("errors")}") + " · ${v.getString("modality")}" +
            (if (s.optJSONObject("parent") != null) "\nrevisão de ${s.getJSONObject("parent").getString("draw_id")}" else "")
        status.setTextColor(if (v.getBoolean("valid")) CYAN else ERR)
        btnReveal.isEnabled = !locked; btnReveal.text = if (locked) "Revelado — travado (use Revisar)" else "Revelar e travar"
        val rows = s.getJSONObject("correspondences").getJSONArray("rows")
        val ps = d.getJSONArray("pieces")
        for (i in 0 until ps.length()) {
            val p = ps.getJSONObject(i); val row = rows.getJSONObject(i)
            val cell = tv("#${p.getInt("position")}\n${p.getInt("top")}\n—\n${p.getInt("bottom")}\nΣ${p.getInt("sum")}", 16f, mono = true).apply {
                gravity = Gravity.CENTER; setTextIsSelectable(false); setPadding(20, 12, 20, 12)
                background = GradientDrawable().apply { setStroke(3, if (row.isNull("evidence")) Color.DKGRAY else METAL[row.getString("evidence")]!!); cornerRadius = 12f }
                setOnClickListener { pieceDetail(p, row, s) }
                if (locked) { alpha = 0f; animate().alpha(1f).setStartDelay(80L * i).setDuration(250).start() } // só após resultado calculado
            }
            mesa.addView(cell, LinearLayout.LayoutParams(-2, -2).apply { setMargins(6, 6, 6, 6) })
        }
        val c = d.getJSONObject("calculated"); val g = d.getJSONObject("generation")
        calc.text = "U=${c.getInt("upper_line_sum")} L=${c.getInt("lower_line_sum")} T=${c.getInt("total_sum")} (recalculado)\n" +
            "geração: ${g.toString(1)}\ndata_hash: ${ver.optString("data_hash")}"
        val cr = s.getJSONObject("correspondences")
        corr.text = "matriz ${cr.getString("matrix_version")} · política ${cr.getJSONObject("isopsephy_policy").getString("id")}\n" +
            (0 until rows.length()).joinToString("\n") { val r = rows.getJSONObject(it)
                if (r.isNull("evidence")) "[—] ${r.getString("slot")}=${r.getInt("index")}: ${r.getString("status")}"
                else { val e = r.getString("evidence"); "[$e ${METAL_NAME[e]}] ${r.getString("slot")}=${r.getInt("index")}: ${r.optString("label")}" } }
        reading.text = if (s.isNull("reading")) "(sem leitura — preenchida no reveal)" else s.getJSONObject("reading").getString("text")
        hashView.text = s.getJSONObject("audit").optString("hash").takeIf { it.isNotEmpty() && it != "null" } ?: "— (gerado no reveal)"
    }

    private fun pieceDetail(p: JSONObject, row: JSONObject, s: JSONObject) {
        val cr = s.getJSONObject("correspondences")
        val ev = if (row.isNull("evidence")) "nenhuma (lacuna)" else "${row.getString("evidence")} (${METAL_NAME[row.getString("evidence")]})"
        msg("Peça #${p.getInt("position")} (${p.getString("id")})",
            "orientação registrada: topo ${p.getInt("top")} / base ${p.getInt("bottom")}\nsoma s${p.getInt("position")} = ${p.getInt("sum")}\n\n" +
            "status: ${row.getString("status")}\nclasse: $ev\ntermo grego / decomposição isopséfica: " +
            (if (row.isNull("evidence")) "não há termo na matriz — nada a decompor (não inventado)" else row.optString("arithmetic")) +
            "\nmatriz: ${cr.getString("matrix_version")}\npolítica: ${cr.getJSONObject("isopsephy_policy").toString(1)}")
    }

    private fun reviseDialog() {
        val s = state ?: return; val e = EditText(this).apply { hint = "motivo (obrigatório)" }
        AlertDialog.Builder(this).setTitle("Revisar").setView(e).setPositiveButton("Criar v+1") { _, _ -> set(Core.call(this, "revise", s.toString(), e.text.toString())) }.setNegativeButton("Cancelar", null).show()
    }
    private fun export() {
        val s = state ?: return; val txt = s.toString(2); copy("drawstate", txt)
        File(getExternalFilesDir(null), "drawstate-${s.getString("draw_id")}.json").writeText(txt, Charsets.UTF_8)
        startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply { type = "application/json"; putExtra(Intent.EXTRA_TEXT, txt) }, "Exportar DrawState"))
    }
    private fun import() {
        val cm = getSystemService(ClipboardManager::class.java); val txt = cm.primaryClip?.getItemAt(0)?.text?.toString() ?: return msg("Importar", "área de transferência vazia")
        val r = Core.call(this, "verify", txt)
        if (!r.getBoolean("ok")) return msg("Importar rejeitado", r.getString("error"))
        state = JSONObject(txt); stateFile.writeText(txt, Charsets.UTF_8); render(); msg("Importado", r.toString(2))
    }
    private fun copy(label: String, t: String) { getSystemService(ClipboardManager::class.java).setPrimaryClip(ClipData.newPlainText(label, t)); Toast.makeText(this, "copiado", Toast.LENGTH_SHORT).show() }
    private fun msg(t: String, m: String) { AlertDialog.Builder(this).setTitle(t).setMessage(m).setPositiveButton("OK", null).show() }
}
