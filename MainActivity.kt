package com.example.resultsapp

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.resultsapp.databinding.ActivityMainBinding
import com.squareup.moshi.Moshi
import com.squareup.moshi.Types
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.Locale

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private val adapter = ResultsAdapter()
    private var allResults: List<ResultItem> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.recycler.layoutManager = LinearLayoutManager(this)
        binding.recycler.adapter = adapter

        loadJson()

        binding.btnSearch.setOnClickListener {
            val q = binding.etQuery.text.toString().trim()
            if (q.isEmpty()) {
                Toast.makeText(this, "أدخل رقم الجلوس أو الاسم", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val normalized = normalizeArabicDigits(q)
            searchAndShow(normalized)
        }
    }

    private fun loadJson() {
        try {
            val input = assets.open("results.json")
            val text = BufferedReader(InputStreamReader(input, "UTF-8")).use { it.readText() }
            val moshi = Moshi.Builder().build()
            val type = Types.newParameterizedType(ResultsFile::class.java)
            // سنستخدم Moshi مباشرة مع adapter generic:
            val listType = Types.newParameterizedType(ResultsFile::class.java)
            val adapterM = moshi.adapter(ResultsFile::class.java)
            val resultsFile = adapterM.fromJson(text)
            allResults = resultsFile?.results ?: emptyList()
            adapter.submitList(emptyList())
        } catch (ex: Exception) {
            ex.printStackTrace()
            Toast.makeText(this, "خطأ في تحميل البيانات: ${ex.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun searchAndShow(q: String) {
        val results = mutableListOf<ResultItem>()
        // إذا كان رقمًا بالكامل: مطابقة رقم الجلوس بالضبط
        if (q.all { it.isDigit() }) {
            results.addAll(allResults.filter { it.number.replace("\\s+".toRegex(), "") == q })
        }
        // بحث عن اسم جزئي (حسّاس لحالة الحروف غير مطلوب)
        results.addAll(allResults.filter { it.name.lowercase(Locale.getDefault()).contains(q.lowercase(Locale.getDefault())) })

        if (results.isEmpty()) {
            Toast.makeText(this, "لا توجد نتائج مطابقة", Toast.LENGTH_SHORT).show()
            adapter.submitList(emptyList())
        } else {
            adapter.submitList(results)
        }
    }

    private fun normalizeArabicDigits(s: String): String {
        val trans = mapOf('٠' to '0','١' to '1','٢' to '2','٣' to '3','٤' to '4','٥' to '5','٦' to '6','٧' to '7','٨' to '8','٩' to '9')
        val sb = StringBuilder()
        for (ch in s) sb.append(trans[ch] ?: ch)
        return sb.toString()
    }
}

ResultsAdapter.kt (RecyclerView)

package com.example.resultsapp

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.resultsapp.databinding.ItemResultBinding

class ResultsAdapter : ListAdapter<ResultItem, ResultsAdapter.VH>(DIFF) {
    companion object {
        val DIFF = object : DiffUtil.ItemCallback<ResultItem>() {
            override fun areItemsTheSame(oldItem: ResultItem, newItem: ResultItem) = oldItem.number == newItem.number && oldItem.year == newItem.year
            override fun areContentsTheSame(oldItem: ResultItem, newItem: ResultItem) = oldItem == newItem
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val binding = ItemResultBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return VH(binding)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val it = getItem(position)
        holder.bind(it)
    }

    inner class VH(private val b: ItemResultBinding) : RecyclerView.ViewHolder(b.root) {
        fun bind(it: ResultItem) {
            b.tvName.text = it.name
            b.tvNumber.text = "رقم: ${it.number}  •  سنة: ${it.year}"
            // عرض الحقول الإضافية كخط واحد مختصر (يمكن توسيعها)
            val extras = it.fields.entries.joinToString("\n") { "${it.key}: ${it.value}" }
            b.tvFields.text = extras
        }
    }
}
