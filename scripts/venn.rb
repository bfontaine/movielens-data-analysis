#! /usr/bin/env ruby
# -*- coding: UTF-8 -*-

require "json"

genres = File.readlines("data/u.genre").map { |line| line.split("|")[0] }
movies = File.readlines("data/u.item").map do |line|
    line.force_encoding("iso-8859-1").split("|")[6..-1].map { |c| c == "1" }
end

sets = {}

movies.each do |movie|
    movie_genres = movie.map.with_index do |ok, i|
        genres[i] if ok
    end.compact.sort

    sets[movie_genres] ||= 0
    sets[movie_genres] += 1
end

venn_sets = sets.map { |names, count| {"sets" => names, "size" => count } }
print venn_sets.to_json
