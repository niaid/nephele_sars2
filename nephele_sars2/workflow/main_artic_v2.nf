/*  COVID-19 Pipeline
 *
 *  Adapted from script from Mohammed Khalfan < mkhalfan@nyu.edu >
 *  NYU Center for Genetics and System Biology 2020
 *
 *  Changes made to run using single pool artic protocol reads
 */

// setting some defaults here,
// can be overridden in config or via command line
params.out = "${params.outputs_dir}"
params.singleEnd = params.data_type=="SE" ? true : false
// params.snpEff_config = "${params.snpeff}"
// println "inputs dir: $params.inputs_dir"
println "mapping file: $params.map_file"
println "singleEnd: $params.singleEnd"
println "outdir: $params.out"

ref = file(params.ref_db_path)

// Reading mapping --> generate pairs of: sample ID, sequences and primer files
map_file = file(params.map_file)
pairs = []
lines  = map_file.readLines()
for( line : lines ) {
    if(line == null || line.isEmpty()) {
        continue
    }
    row = line.split("\t")
    if(row[0] == "#SampleID" || row[0] == "Description") {
        continue
    } else {
        if (params.singleEnd) {
            pair = [row[0], [row[1]], params.primer_file_path]
            pairs.add(pair)

        } else {
            pair = [row[0], [row[1], row[2]], params.primer_file_path]
            pairs.add(pair)
        }
    }
}

println "pairs: $pairs"

Channel
    .fromList(pairs)
    .set { read_pairs_ch }

if (params.singleEnd) {
    process trim_se {
        publishDir "${params.out}/trimmed", mode:'copy'
        errorStrategy 'finish'

        input:
        tuple sample_id, reads, primer from read_pairs_ch

        output:
        tuple val(sample_id),
        file("${sample_id}_trimmed_1.fq.gz") into trimmed_ch

        script:
        """
        trimmomatic SE \
            -phred33 \
            -threads ${task.cpus} \
            ${reads[0]} \
            ${sample_id}_trimmed_1.fq.gz \
            ILLUMINACLIP:${params.adapters}:2:30:10:8:true \
            LEADING:20 TRAILING:20 SLIDINGWINDOW:4:20 MINLEN:20
        """
    }
    process align_se {
        publishDir "${params.out}/aligned_reads", mode:'copy'
        errorStrategy 'finish'

        input:
        tuple sample_id, file(read_1) from trimmed_ch

        output:
        // val(pair_id_unmerged) into jbrowse_pair_id_ch
        // tuple val(sample_id), file("${sample_id}_aligned_reads.sam") into merged_bam_ch
        tuple val(sample_id), file("${sample_id}_aln.bam") into raw_bam_ch

        tuple val(sample_id),
           file("${sample_id}_aln.bam"),
           file("${sample_id}_aln.bam.bai") into individual_bw_ch

        script:
        // sample_id=pair_id - ~/${params.grouping_regex}/
        // pair_id_unmerged=sample_id + "_${pool}_unmerged"
        readGroup = "@RG\\tID:${sample_id}\\tLB:${sample_id}\\tPL:${params.pl}\\tPM:${params.pm}\\tSM:${sample_id}"
        """
        bwa mem \
            -K 100000000 \
            -v 3 -t ${task.cpus} \
            -Y \
            -R \"${readGroup}\" \
            $ref \
            $read_1 \
            | samtools sort -o ${sample_id}_aln.bam

        samtools index ${sample_id}_aln.bam
        """
    }
} else {
    process trim_pe {
        publishDir "${params.out}/trimmed", mode:'copy'
        errorStrategy 'finish'

        input:
        tuple sample_id, reads, primer from read_pairs_ch

        output:
        tuple val(sample_id),
            file("${sample_id}_trimmed_1.fq.gz"),
            file("${sample_id}_trimmed_2.fq.gz") into trimmed_ch

        script:
        """
        trimmomatic PE \
            -phred33 \
            -threads ${task.cpus} \
            ${reads[0]} \
            ${reads[1]} \
            ${sample_id}_trimmed_1.fq.gz \
            ${sample_id}.unpair_trimmed_1.fq.gz \
            ${sample_id}_trimmed_2.fq.gz \
            ${sample_id}.unpair_trimmed_2.fq.gz \
            ILLUMINACLIP:${params.adapters}:2:30:10:8:true \
            LEADING:20 TRAILING:20 SLIDINGWINDOW:4:20 MINLEN:20
        """
    }
    process align_pe {
        publishDir "${params.out}/aligned_reads", mode:'copy'
        errorStrategy 'finish'

        input:
        tuple sample_id, file(read_1), file(read_2) from trimmed_ch

        output:
        // val(pair_id_unmerged) into jbrowse_pair_id_ch
        // tuple val(sample_id), file("${sample_id}_aligned_reads.sam") into merged_bam_ch
        tuple val(sample_id), file("${sample_id}_aln.bam") into raw_bam_ch

        tuple val(sample_id),
           file("${sample_id}_aln.bam"),
           file("${sample_id}_aln.bam.bai") into individual_bw_ch

        script:
        // sample_id=pair_id - ~/${params.grouping_regex}/
        // pair_id_unmerged=sample_id + "_${pool}_unmerged"
        readGroup = "@RG\\tID:${sample_id}\\tLB:${sample_id}\\tPL:${params.pl}\\tPM:${params.pm}\\tSM:${sample_id}"

        """
        bwa mem \
            -K 100000000 \
            -v 3 -t ${task.cpus} \
            -Y \
            -R \"${readGroup}\" \
            $ref \
            $read_1 \
            $read_2 \
            | samtools sort -o ${sample_id}_aln.bam

        samtools index ${sample_id}_aln.bam
        """
    }
}

process primer_trim {
    publishDir "${params.out}/bam_files", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id), file(bam) from raw_bam_ch

    output:
    tuple val(sample_id), file("${sample_id}_aln_ptrim_sort.bam") into trim_bam_ch,
        to_downsample_bam_ch,
        trim_bam_metrics_ch,
        trim_bam_metrics_ch_insert

    script:
    """
    ivar trim -e -i ${bam} -b ${params.primer_file_path} -p ${sample_id}_aln_ptrim
    samtools sort -o ${sample_id}_aln_ptrim_sort.bam ${sample_id}_aln_ptrim.bam
    samtools index ${sample_id}_aln_ptrim_sort.bam
    """
}

process downsample_bam{
    publishDir "${params.out}/aligned_reads", mode:'copy'
    errorStrategy 'finish'
    input:
    tuple val(sample_id), file(bam) from to_downsample_bam_ch

    output:
    tuple val(sample_id), file("${sample_id}_ptrim_down_sort.bam") into downsample_bam_ch,
        downsample_bam_metrics_ch,
        raw_consensus_bam_ch,
        downsample_bam_reads_ch

    script:
    """
    jvarkit sortsamrefname \
        --samoutputformat BAM \
        $bam |\
    jvarkit biostar154220 \
        -n 200 \
        --samoutputformat BAM |\
        samtools sort -o ${sample_id}_ptrim_down_sort.bam

    samtools index ${sample_id}_ptrim_down_sort.bam
    """
}

process haplotypeCaller {
    errorStrategy 'finish'
    input:
    tuple val(sample_id), file(preprocessed_bam) from downsample_bam_ch

    output:
    tuple val(sample_id), file("${sample_id}_raw_variants.vcf") into hc_output_ch

    tuple val(hc_bamout_sample_id),
        file("${sample_id}_haplotypecaller_bamout.bam"),
        file("${sample_id}_haplotypecaller_bamout.bai") into hc_bam_bw_ch

    script:
    hc_bamout_sample_id = sample_id + "-hc_bamout"
    """
    gatk HaplotypeCaller \
        -R $ref \
        -I $preprocessed_bam \
        -O ${sample_id}_raw_variants.vcf \
        -bamout ${sample_id}_haplotypecaller_bamout.bam \
        -ploidy 1
    """
}

process selectVariants {
    errorStrategy 'finish'
    input:
    tuple val(sample_id), file(raw_variants) from hc_output_ch

    output:
    tuple val(sample_id), file("${sample_id}.snps.vcf") into raw_snps_ch, raw_snps_qc_ch
    tuple val(sample_id), file("${sample_id}.indels.vcf") into raw_indels_ch

    script:
    """
    gatk SelectVariants \
        -R $ref \
        -V $raw_variants \
        -select-type SNP \
        -O ${sample_id}.snps.vcf

    gatk SelectVariants \
        -R $ref \
        -V $raw_variants \
        -select-type INDEL \
        -O ${sample_id}.indels.vcf
    """
}

process filterSnps {
    publishDir "${params.out}/filtered_variants", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id), file(raw_snps) from raw_snps_ch

    output:
    tuple val(sample_id),
        file("${sample_id}.filt.snps.vcf"),
        file("${sample_id}.filt.snps.vcf.idx") into filtered_snps_qc_ch



    script:
    """
    gatk VariantFiltration \
    -R $ref \
    -V $raw_snps \
    -O ${sample_id}.filt.snps.vcf \
        -filter-name "DP_filter" -filter "DP < 10.0" \
        -filter-name "QD_filter" -filter "QD < 2.0" \
        -filter-name "FS_filter" -filter "FS > 100.0" \
        -filter-name "MQ_filter" -filter "MQ < 40.0" \
        -filter-name "SOR_filter" -filter "SOR > 4.0" \
        -filter-name "ReadPosRankSum_filter" -filter "ReadPosRankSum < -8.0"
    """
}

process filterIndels {
    publishDir "${params.out}/filtered_variants", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id), file(raw_indels) from raw_indels_ch

    output:
    tuple val(sample_id),
        file("${sample_id}.filt.indels.vcf"),
        file("${sample_id}.filt.indels.vcf.idx") into filtered_indels_qc_ch

    script:
    """
    gatk VariantFiltration \
        -R $ref \
        -V $raw_indels \
        -O ${sample_id}.filt.indels.vcf \
        -filter-name "DP_filter" -filter "DP < 20.0" \
        -filter-name "QD_filter" -filter "QD < 2.0" \
        -filter-name "FS_filter" -filter "FS > 200.0" \
        -filter-name "SOR_filter" -filter "SOR > 4.0"
    """
}

// combine
// filtered_snps_qc_ch.join(filtered_indels_qc_ch)
//     .set{ variants_filtered }

process combineVariants {
    publishDir "${params.out}/filtered_variants", mode:'copy'
    errorStrategy 'finish'
    // saveAs: {filename -> params.saveIntermediateVariants ? "$filename" : null }

    input:
    tuple val(sample_id), file(fsnp), file(fsnp_idx), file(findel), file(findel_idx) from filtered_snps_qc_ch
        .join(filtered_indels_qc_ch)

    output:
    tuple val(sample_id), file("${sample_id}.filt.vars.vcf") into combined_variants_gatk_ch, consensus_filtered_vars_ch

    script:
    """
    picard MergeVcfs \
        -I ${fsnp} \
        -I ${findel} \
        -O ${sample_id}.filt.vars.vcf \
    """
}

process snpEff{
    publishDir "${params.out}/variant_files", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id), file(variants) from combined_variants_gatk_ch

    output:
    file '*' into snpeff_out
    file("${sample_id}.filt.vars.ann.vcf.gz") into snpeff_bzip_tabix_vcf_ch
    tuple val(sample_id), file("${sample_id}.filt.vars.ann.vcf.gz") into vcf_metrics, vcf_to_parse

    script:
    """
    java -jar ${params.snpeffjar} -v \
        -c ${params.snpeff} -dataDir ${params.snpeff_db_path} \
        -v -no-downstream -no-upstream \
        -s ${sample_id}_snpEff_summary.html \
        ${params.snpeffref} \
        $variants > ${sample_id}.filt.vars.ann.vcf

    bgzip ${sample_id}.filt.vars.ann.vcf
    bgzip ${sample_id}.filt.vars.vcf
    """
}

process getMetrics {
    publishDir "${params.out}/metrics", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id), file(trim_bam), file(down_bam), file(vcf) from trim_bam_metrics_ch
        .join(downsample_bam_metrics_ch)
        .join(vcf_metrics)

    output:
    tuple val(sample_id),
            file("${sample_id}_alignment_metrics.txt"),
            file("${sample_id}_depth_out.txt"),
            file("${sample_id}_vcf_stats.txt") into metrics_output

    tuple val(sample_id),
            file("${sample_id}_down_alignment_metrics.txt"),
            file("${sample_id}_down_depth_out.txt") into down_metrics_output

    tuple val(sample_id), file("${sample_id}_depth_out.txt") into raw_coverage_ch
    tuple val(sample_id), file("${sample_id}_down_depth_out.txt") into down_coverage_ch

    script:
    """
    picard \
        CollectAlignmentSummaryMetrics \
        R=${params.ref_db_path} \
        I=${trim_bam} \
        O=${sample_id}_alignment_metrics.txt

    samtools depth -a ${trim_bam} > ${sample_id}_depth_out.txt

    picard \
        CollectAlignmentSummaryMetrics \
        R=${params.ref_db_path} \
        I=${down_bam} \
        O=${sample_id}_down_alignment_metrics.txt

    samtools depth -a ${down_bam} > ${sample_id}_down_depth_out.txt

    bcftools stats $vcf > ${sample_id}_vcf_stats.txt
    """
}

if (!params.singleEnd) {
    process getMetrics_insert {
        publishDir "${params.out}/metrics", mode:'copy'
        errorStrategy 'finish'

        input:
        tuple val(sample_id), file(trim_bam) from trim_bam_metrics_ch_insert

        output:
        tuple val(sample_id),
                file("${sample_id}_insert_metrics.txt"),
                file("${sample_id}_insert_size_histogram.pdf") into metrics_output_insert

        script:
        """
        picard \
            CollectInsertSizeMetrics \
            INPUT=${trim_bam} \
            OUTPUT=${sample_id}_insert_metrics.txt \
            HISTOGRAM_FILE=${sample_id}_insert_size_histogram.pdf
        """
    }
}

process plot_coverage {
    publishDir "${params.out}/metrics", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id), file(raw_cov), file(down_cov) from raw_coverage_ch
        .join(down_coverage_ch)

    output:
    tuple file("${sample_id}_coverage_plot.pdf"), file("${sample_id}_coverage_plot.png") into coverage_out

    script:
    """
    python3 ${params.plot_coverage} --sample $sample_id --full $raw_cov --down $down_cov --out1 ${sample_id}_coverage_plot.pdf --out2 ${sample_id}_coverage_plot.png
    """
}

process qc {
    publishDir "${params.out}/reports_ind", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id),
        file(aln_stats),
        file(depth_stats),
        file(vcf_stats) from metrics_output

    output:
    file("${sample_id}_report.csv") into parse_metrics_output

    script:
    """
    python3 ${params.parse_metrics_artic} --sample $sample_id --aln-stats $aln_stats --depth $depth_stats --vcf-stats $vcf_stats --out ${sample_id}_report.csv
    """
}

/* Process qc above creates a report for each sample.
 * Below we compile these into a single report.
 */
parse_metrics_output.collectFile(name: "${workflow.runName}_report.csv", keepHeader: true, storeDir: "${params.out}/reports")


process snpeff_effect {
    publishDir "${params.out}/reports_ind", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id),
        file(vcf) from vcf_to_parse

    output:
    file("${sample_id}_variant_effect.csv") into parse_vcf_output

    script:
    """
    python3 ${params.parse_snpeff_effect} --sample $sample_id --in_vcf $vcf --out ${sample_id}_variant_effect.csv
    """
}

// collate snpeff_effect results into single file
parse_vcf_output.collectFile(name: "${workflow.runName}_snpeff_variant_report.csv", keepHeader: true, storeDir: "${params.out}/reports")


// generate consensus
process raw_consensus {
    publishDir "${params.out}/raw_consensus", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id), file(filtered_vars), file(bam) from consensus_filtered_vars_ch
        .join(raw_consensus_bam_ch)

    output:
    tuple val(sample_id), file("${sample_id}_raw.fasta") into raw_consensus_ch, raw_consensus_ref_ch
    file '*' into raw_consensus_index_ch

    script:
    """
    gatk IndexFeatureFile -I $filtered_vars

    gatk FastaAlternateReferenceMaker \
        -R $ref \
        -O ${sample_id}_raw.fasta \
        -V $filtered_vars

    # chromosome ID needs to match ID in bam for bedtools (maskfasta)
    sed -i 's/1 NC_045512.2:1-29903/${sample_id}/g' ${sample_id}_raw.fasta

    bwa index ${sample_id}_raw.fasta
    """
}

// map reads to raw_consensus to get coverage
if (params.singleEnd) {
    process extract_downsample_reads_se {
        input:
        tuple val(sample_id), file(bam) from downsample_bam_reads_ch

        output:
        tuple val(sample_id), file("${sample_id}_down.fq.gz") into downsample_reads_ch

        script:
        """
        samtools fastq $bam -0 ${sample_id}_down.fq.gz
        """
    }
    process align_down_se {
        publishDir "${params.out}/raw_consensus_bam", mode:'copy'
        errorStrategy 'finish'

        input:
        tuple sample_id, file(consensus_hold), file(read_1) from raw_consensus_ch
            .join(downsample_reads_ch)

        output:
        tuple val(sample_id), file("${sample_id}_consensus_aln.bam") into consensus_bam_ch

        script:
        readGroup = "@RG\\tID:${sample_id}\\tLB:${sample_id}\\tPL:${params.pl}\\tPM:${params.pm}\\tSM:${sample_id}"
        consensus_ref = "${params.out}/raw_consensus/${sample_id}_raw.fasta"

        """
        bwa mem \
            -K 100000000 \
            -v 3 -t ${task.cpus} \
            -Y \
            -R \"${readGroup}\" \
            $consensus_ref \
            $read_1 \
            | samtools sort -o ${sample_id}_consensus_aln.bam

        samtools index ${sample_id}_consensus_aln.bam
        """
    }
} else {
    process extract_downsample_reads_pe {
        input:
        tuple val(sample_id), file(bam) from downsample_bam_reads_ch

        output:
        tuple val(sample_id), file("${sample_id}_down_1.fq.gz"), file("${sample_id}_down_2.fq.gz") into downsample_reads_ch

        script:
        """
        samtools sort -n $bam | samtools fastq - -1 ${sample_id}_down_1.fq.gz -2 ${sample_id}_down_2.fq.gz -s ${sample_id}_singletons.
        """
    }
    process align_down_pe {
        publishDir "${params.out}/raw_consensus_bam", mode:'copy'
        errorStrategy 'finish'

        input:
        tuple sample_id, file(consensus_hold), file(read_1), file(read_2) from raw_consensus_ch
            .join(downsample_reads_ch)

        output:
        tuple val(sample_id), file("${sample_id}_consensus_aln.bam") into consensus_bam_ch

        script:
        readGroup = "@RG\\tID:${sample_id}\\tLB:${sample_id}\\tPL:${params.pl}\\tPM:${params.pm}\\tSM:${sample_id}"
        consensus_ref = "${params.out}/raw_consensus/${sample_id}_raw.fasta"

        """
        bwa mem \
            -K 100000000 \
            -v 3 -t ${task.cpus} \
            -Y \
            -R \"${readGroup}\" \
            $consensus_ref \
            $read_1 \
            $read_2 \
            | samtools sort -o ${sample_id}_consensus_aln.bam

        samtools index ${sample_id}_consensus_aln.bam
        """
    }
}

process consensus {
    publishDir "${params.out}/consensus", mode:'copy'
    errorStrategy 'finish'

    input:
    tuple val(sample_id), file(raw_ref), file(bam) from raw_consensus_ref_ch
        .join(consensus_bam_ch)

    output:
    file("${sample_id}*.fasta") into consensus_ch

    script:
    """
    for x in {10,20}; do
        # make bedfile with regions below x coverage
        # genomecov generates bedgraph file
        # genomecov input is filtered for min MAPQ (20)
        # and to remove dups and non-primary alignments
        # first awk filters bedgraph for coverage <= x
        # second awk converts bedgraph to 3-col bedfile

        samtools view -bq 20 -F 1284 $bam \
            | bedtools genomecov -ibam stdin -bga \
            | awk -v threshold="\$x" '\$4<threshold' \
            | awk '{print \$1 "\t" \$2 "\t" \$3}' > ${sample_id}_below_\${x}_cov.bed

        # mask all regions in bedfile produced above
        bedtools maskfasta \
            -fi ${sample_id}_raw.fasta \
            -bed ${sample_id}_below_\${x}_cov.bed \
            -fo ${sample_id}_below_\${x}_masked.fasta

        # rename the fasta header from ref name to sample id
        # sed -i 's/NC_045512.2/${sample_id}/g' ${sample_id}_below_\${x}_masked.fasta
    done
    """
}
