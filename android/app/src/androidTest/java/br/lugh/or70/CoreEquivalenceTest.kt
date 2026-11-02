package br.lugh.or70

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

/** Valores de referência gerados pelo CLI Python no host (ver docs/ANDROID-CONTRATO.md). */
@RunWith(AndroidJUnit4::class)
class CoreEquivalenceTest {
    private val ctx get() = InstrumentationRegistry.getInstrumentation().targetContext
    private fun c(fn: String, vararg a: Any) = Core.call(ctx, fn, *a)

    @Test fun seed70_dataHash_equalsHostCli() {
        val r = c("draw_seed", 70, 7); assertTrue(r.getBoolean("ok"))
        assertEquals("74f10b287ac8c25fd47fe86e65c88cbdc894ef52f647ac0ae0b406bb34d648c5", r.getString("data_hash"))
        assertEquals(53, r.getJSONObject("state").getJSONObject("data").getJSONObject("calculated").getInt("total_sum"))
    }
    @Test fun physical_preservesOrientation_andHash() {
        val r = c("draw_physical", "3/4,4/0,5/2,4/2,5/1,5/4,5/5")
        assertEquals("5bfcdc8bffb497d5349b2b0239138dd6daa86ed86f3d014463828bb6c4d1f5e5", r.getString("data_hash"))
        val p = r.getJSONObject("state").getJSONObject("data").getJSONArray("pieces").getJSONObject(1)
        assertEquals(2, p.getInt("position")); assertEquals(4, p.getInt("top")); assertEquals(0, p.getInt("bottom"))
    }
    @Test fun invalid_inputs() {
        assertFalse(c("draw_physical", "3/x,1/2").getBoolean("ok"))
        val dup = c("draw_physical", "3/4,4/3,1/1,2/2,5/5,6/6,0/1").getJSONObject("state").getJSONObject("data").getJSONObject("validation")
        assertFalse(dup.getBoolean("valid"))
        val face = c("draw_physical", "7/1,1/1,2/2,3/3,4/4,5/5,6/6").getJSONObject("state").getJSONObject("data").getJSONObject("validation")
        assertFalse(face.getBoolean("valid"))
    }
    @Test fun lock_blocksEdits_persists_reimports_andRevises() {
        val st = c("reveal", c("draw_seed", 70, 7).getJSONObject("state").toString()).getJSONObject("state")
        val hash = st.getJSONObject("audit").getString("hash")
        val f = File(ctx.filesDir, "test_persist.json"); f.writeText(st.toString(2), Charsets.UTF_8)
        val reloaded = f.readText(Charsets.UTF_8)  // simula fechar/reabrir: estado vem do arquivo
        val edit = c("try_set_reading", reloaded, "x"); assertFalse(edit.getBoolean("ok")); assertTrue(edit.getString("error").startsWith("LockedError"))
        assertTrue(c("reveal", reloaded).getString("error").startsWith("LockedError"))
        val v = c("verify", reloaded); assertTrue(v.getBoolean("hash_ok")); assertEquals(true, v.get("reproduz"))
        assertEquals(hash, JSONObject(reloaded).getJSONObject("audit").getString("hash"))
        val tampered = JSONObject(reloaded).apply { getJSONObject("reading").put("text", "adulterado") }
        assertFalse(c("verify", tampered.toString()).getBoolean("hash_ok"))
        val rv = c("revise", reloaded, "teste"); val n = rv.getJSONObject("state")
        assertEquals(2, n.getInt("version")); assertEquals(hash, n.getJSONObject("parent").getString("hash"))
        assertFalse(c("revise", reloaded, "").getBoolean("ok"))
    }
}
