using Pkg

using CSV
using DataFrames

team_ots = CSV.read("team_agrup.csv", DataFrame)


function jaccard(a::DataFrameRow, b::DataFrameRow)
    # Convertir los DataFrames a vectores unidimensionales
    a_vec = Vector(a)
    b_vec = Vector(b)
    
    # Calcular la intersección
    intersection = length(intersect(a_vec, b_vec))
    
    # Calcular la unión
    union2 = length(union(a_vec, b_vec))
    
    # Calcular la similitud de Jaccard
    jaccard = 1 - intersection / union2
    
    return jaccard
end

jaccard(team_ots[1, :], team_ots[2, :])

function jacc_mat(a::DataFrame , n::Int64)
    # Convertir los DataFrames a vectores unidimensionales
    #n = length(a)
    distances_matrix = zeros(Float64, n, n)

    for i in 1:n
        for j in i+1:n
            distancia_jaccard = jaccard(a[i, :], a[j, :])
            distances_matrix[i, j] = distancia_jaccard
            distances_matrix[j, i] = distancia_jaccard
        end
    end
    return distances_matrix
end

dist_matrix=jacc_mat(team_ots, 5074)
dist_matrix
DataFrame(Tables.table(dist_matrix))
CSV.write("jacc_matrix_fix.csv", DataFrame(Tables.table(dist_matrix)))

